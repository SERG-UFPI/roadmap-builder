"""Levantamento de requisitos (PerSpecML) por projeto.

Uma especificação por funcionalidade de ML; cada concern do catálogo passa
pela verificação de aplicabilidade e, se aplicável, é especificado.
Não depende do GitHub (funciona sem PAT).
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.app.db import get_db
from backend.app.deps import require_user
from backend.app.models import ConcernSpec, Project, RequirementsSpec, User, _utcnow
from backend.app.routers.projects import _project_or_404
from backend.app.services.perspecml_catalog import (
    CATALOG_ID,
    CATALOG_VERSION,
    concerns_by_id,
    get_catalog,
    ordered_concern_ids,
    related_map,
)
from backend.app.services.perspecml_template import EXAMPLE_SPEC
from backend.app.services.requirements import (
    APPLICABILITY,
    concern_dict,
    export_markdown,
    progress,
    relation_alerts,
    stakeholders,
)

router = APIRouter(prefix="/api", tags=["requirements"])

_ROLE_IDS = {s["id"] for s in get_catalog()["stakeholders"]}


class SpecCreate(BaseModel):
    title: str = Field(min_length=1, max_length=512)
    user_story: str = ""
    description: str = ""


class SpecUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=512)
    user_story: str | None = None
    description: str | None = None
    stakeholders: dict[str, str] | None = None


class ConcernUpdate(BaseModel):
    applicability: str | None = None
    specification: str | None = None
    notes: str | None = None
    needs_refinement: bool | None = None


def _spec_or_404(db: Session, project: Project, spec_id: int) -> RequirementsSpec:
    s = db.get(RequirementsSpec, spec_id)
    if s is None or s.project_id != project.id:
        raise HTTPException(status_code=404, detail="Especificação não encontrada.")
    return s


def _entries(db: Session, spec: RequirementsSpec) -> dict[str, ConcernSpec]:
    rows = db.execute(select(ConcernSpec).where(ConcernSpec.spec_id == spec.id)).scalars()
    return {r.concern_id: r for r in rows}


def _spec_summary(spec: RequirementsSpec, entries: dict[str, ConcernSpec]) -> dict:
    return {
        "id": spec.id,
        "project_id": spec.project_id,
        "title": spec.title,
        "user_story": spec.user_story,
        "description": spec.description,
        "catalog": spec.catalog,
        "catalog_version": spec.catalog_version,
        "stakeholders": stakeholders(spec),
        "created_at": spec.created_at.isoformat() if spec.created_at else None,
        "updated_at": spec.updated_at.isoformat() if spec.updated_at else None,
        "progress": progress(entries),
    }


def _spec_full(spec: RequirementsSpec, entries: dict[str, ConcernSpec]) -> dict:
    out = _spec_summary(spec, entries)
    out["concerns"] = {cid: concern_dict(entries.get(cid), cid) for cid in ordered_concern_ids()}
    out["alerts"] = relation_alerts(entries)
    return out


@router.get("/requirements/catalog")
def catalog(user: User = Depends(require_user)):
    cat = get_catalog()
    return cat | {"related": related_map()}


@router.get("/projects/{project_id}/requirements")
def list_specs(
    project_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    project = _project_or_404(db, user, project_id)
    specs = (
        db.execute(
            select(RequirementsSpec)
            .where(RequirementsSpec.project_id == project.id)
            .order_by(RequirementsSpec.created_at.desc())
        )
        .scalars()
        .all()
    )
    return [_spec_summary(s, _entries(db, s)) for s in specs]


@router.post("/projects/{project_id}/requirements")
def create_spec(
    project_id: int,
    payload: SpecCreate,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    project = _project_or_404(db, user, project_id)
    spec = RequirementsSpec(
        project_id=project.id,
        created_by_user_id=user.id,
        title=payload.title.strip(),
        user_story=payload.user_story,
        description=payload.description,
        catalog=CATALOG_ID,
        catalog_version=CATALOG_VERSION,
    )
    db.add(spec)
    db.commit()
    db.refresh(spec)
    return _spec_full(spec, {})


@router.post("/projects/{project_id}/requirements/example")
def create_example_spec(
    project_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Cria a especificação de exemplo do template (caso do empréstimo bancário).

    Os concerns com exemplo no template entram como aplicáveis e especificados;
    os demais ficam pendentes.
    """
    project = _project_or_404(db, user, project_id)
    spec = RequirementsSpec(
        project_id=project.id,
        created_by_user_id=user.id,
        title=EXAMPLE_SPEC["title"],
        user_story=EXAMPLE_SPEC["user_story"],
        description=EXAMPLE_SPEC["description"],
        catalog=CATALOG_ID,
        catalog_version=CATALOG_VERSION,
    )
    db.add(spec)
    db.flush()
    for cid in ordered_concern_ids():
        example = concerns_by_id()[cid]["example"]
        if example:
            db.add(
                ConcernSpec(
                    spec_id=spec.id,
                    concern_id=cid,
                    applicability="applicable",
                    specification=example,
                    notes="",
                    updated_by_user_id=user.id,
                )
            )
    db.commit()
    db.refresh(spec)
    return _spec_full(spec, _entries(db, spec))


@router.get("/projects/{project_id}/requirements/{spec_id}")
def get_spec(
    project_id: int,
    spec_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    spec = _spec_or_404(db, _project_or_404(db, user, project_id), spec_id)
    return _spec_full(spec, _entries(db, spec))


@router.patch("/projects/{project_id}/requirements/{spec_id}")
def update_spec(
    project_id: int,
    spec_id: int,
    payload: SpecUpdate,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    spec = _spec_or_404(db, _project_or_404(db, user, project_id), spec_id)
    if payload.title is not None:
        spec.title = payload.title.strip()
    if payload.user_story is not None:
        spec.user_story = payload.user_story
    if payload.description is not None:
        spec.description = payload.description
    if payload.stakeholders is not None:
        unknown = set(payload.stakeholders) - _ROLE_IDS
        if unknown:
            raise HTTPException(
                status_code=422, detail=f"Papéis desconhecidos: {', '.join(sorted(unknown))}."
            )
        spec.stakeholders_json = json.dumps(
            {k: v for k, v in payload.stakeholders.items() if v.strip()}
        )
    db.commit()
    db.refresh(spec)
    return _spec_full(spec, _entries(db, spec))


@router.delete("/projects/{project_id}/requirements/{spec_id}")
def delete_spec(
    project_id: int,
    spec_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    spec = _spec_or_404(db, _project_or_404(db, user, project_id), spec_id)
    db.execute(delete(ConcernSpec).where(ConcernSpec.spec_id == spec.id))
    db.delete(spec)
    db.commit()
    return {"ok": True}


@router.put("/projects/{project_id}/requirements/{spec_id}/concerns/{concern_id}")
def update_concern(
    project_id: int,
    spec_id: int,
    concern_id: str,
    payload: ConcernUpdate,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    spec = _spec_or_404(db, _project_or_404(db, user, project_id), spec_id)
    if concern_id not in concerns_by_id():
        raise HTTPException(status_code=404, detail=f"Concern '{concern_id}' não existe no catálogo.")
    if payload.applicability is not None and payload.applicability not in APPLICABILITY:
        raise HTTPException(status_code=422, detail="Aplicabilidade inválida.")

    entry = db.execute(
        select(ConcernSpec).where(
            ConcernSpec.spec_id == spec.id, ConcernSpec.concern_id == concern_id
        )
    ).scalar_one_or_none()
    if entry is None:
        entry = ConcernSpec(spec_id=spec.id, concern_id=concern_id, applicability="pending",
                            specification="", notes="")
        db.add(entry)
    if payload.applicability is not None:
        entry.applicability = payload.applicability
    if payload.specification is not None:
        entry.specification = payload.specification
    if payload.notes is not None:
        entry.notes = payload.notes
    if payload.needs_refinement is not None:
        entry.needs_refinement = payload.needs_refinement
    entry.updated_by_user_id = user.id
    # toca a especificação para refletir a última edição na lista
    spec.updated_at = entry.updated_at = _utcnow()
    db.commit()
    db.refresh(spec)
    return _spec_full(spec, _entries(db, spec))


@router.get("/projects/{project_id}/requirements/{spec_id}/export")
def export_spec(
    project_id: int,
    spec_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    project = _project_or_404(db, user, project_id)
    spec = _spec_or_404(db, project, spec_id)
    filename, markdown = export_markdown(
        spec, _entries(db, spec), f"{project.owner}/{project.repo}"
    )
    return {"filename": filename, "markdown": markdown}
