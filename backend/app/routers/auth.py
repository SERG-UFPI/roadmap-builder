"""Rotas de autenticação via GitHub OAuth (login apenas)."""

from __future__ import annotations

import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from backend.app import oauth
from backend.app.config import get_settings
from backend.app.db import get_db
from backend.app.deps import get_current_user
from backend.app.models import Project, User, _utcnow
from backend.app.security import issue_session
from backend.app.services.orgs import sync_orgs

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/api/auth", tags=["auth"])


def _set_session_cookie(resp, token: str) -> None:
    resp.set_cookie(
        settings.session_cookie_name,
        token,
        max_age=settings.session_ttl_hours * 3600,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
    )


@router.get("/github/login")
def github_login():
    if not settings.oauth_configured:
        raise HTTPException(
            status_code=503,
            detail="OAuth do GitHub não configurado (defina GITHUB_OAUTH_CLIENT_ID/SECRET).",
        )
    state = oauth.new_state()
    resp = RedirectResponse(oauth.authorize_url(state), status_code=302)
    resp.set_cookie(
        settings.oauth_state_cookie_name,
        state,
        max_age=600,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
    )
    return resp


@router.get("/github/callback")
def github_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    db: Session = Depends(get_db),
):
    expected_state = request.cookies.get(settings.oauth_state_cookie_name)
    if not code or not state or not expected_state or state != expected_state:
        raise HTTPException(status_code=400, detail="Fluxo OAuth inválido (state).")

    try:
        access_token = oauth.exchange_code(code)
        gh_user = oauth.fetch_github_user(access_token)
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("Falha no callback OAuth: %s", exc)
        raise HTTPException(status_code=502, detail="Falha ao autenticar com o GitHub.")

    github_id = int(gh_user["id"])
    user = db.query(User).filter(User.github_id == github_id).one_or_none()
    if user is None:
        user = User(github_id=github_id)
        db.add(user)
    user.login = gh_user.get("login", user.login or "")
    user.name = gh_user.get("name")
    user.email = gh_user.get("email")
    user.avatar_url = gh_user.get("avatar_url")
    user.last_login_at = _utcnow()
    db.commit()
    db.refresh(user)

    # Multi-tenant: sincroniza orgs + papéis com o token OAuth (best-effort;
    # exige `read:org` — se não concedido, o usuário sincroniza depois via PAT).
    try:
        sync_orgs(db, user, access_token)
    except Exception:  # noqa: BLE001
        logger.warning("Sync de orgs no login falhou (seguindo).", exc_info=True)

    resp = RedirectResponse(settings.frontend_url, status_code=302)
    _set_session_cookie(resp, issue_session(user.id))
    resp.delete_cookie(settings.oauth_state_cookie_name, path="/")
    return resp


# Usuário local de desenvolvimento: github_id negativo nunca colide com um id
# real do GitHub.
DEV_GITHUB_ID = -1
DEV_LOGIN = "dev-local"


@router.post("/dev-login")
def dev_login(db: Session = Depends(get_db)):
    """Entra como usuário local, sem GitHub (só com DEV_LOGIN_ENABLED=true).

    Na primeira vez cria o usuário e um projeto de demonstração para que as
    telas que não dependem do GitHub (ex.: requisitos) possam ser validadas.
    """
    if not settings.dev_login_available:
        raise HTTPException(status_code=404, detail="Not Found")

    user = db.query(User).filter(User.github_id == DEV_GITHUB_ID).one_or_none()
    if user is None:
        user = User(github_id=DEV_GITHUB_ID, login=DEV_LOGIN, name="Usuário local (dev)")
        db.add(user)
        db.flush()
        db.add(
            Project(
                created_by_user_id=user.id,
                owner=DEV_LOGIN,
                repo="demo-ml",
                title="Projeto demo (local)",
                source="imported",
                org_login=DEV_LOGIN,
            )
        )
    user.last_login_at = _utcnow()
    db.commit()
    db.refresh(user)

    resp = JSONResponse({"ok": True, "login": user.login})
    _set_session_cookie(resp, issue_session(user.id))
    return resp


@router.post("/logout")
def logout():
    resp = JSONResponse({"ok": True})
    resp.delete_cookie(settings.session_cookie_name, path="/")
    return resp


@router.get("/me")
def me(user: User | None = Depends(get_current_user)):
    if user is None:
        return {"authenticated": False}
    return {
        "authenticated": True,
        "id": user.id,
        "login": user.login,
        "name": user.name,
        "avatar_url": user.avatar_url,
        "has_pat": user.pat_encrypted is not None,
    }
