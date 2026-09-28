"""Testes do módulo de requisitos (PerSpecML) e do login local de dev."""

from __future__ import annotations

import pytest

from backend.app.config import Settings, get_settings
from backend.app.models import ConcernSpec, Project, RequirementsSpec, User
from backend.app.services.perspecml_catalog import (
    concerns_by_id,
    get_catalog,
    ordered_concern_ids,
    related_map,
)
from backend.app.services.perspecml_template import EXAMPLE_SPEC, TEMPLATE


@pytest.fixture
def project(db, user):
    p = Project(created_by_user_id=user.id, owner="octocat", repo="ml", title="ML")
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@pytest.fixture
def spec(auth_client, project):
    r = auth_client.post(
        f"/api/projects/{project.id}/requirements",
        json={"title": "Análise de reviews", "user_story": "Como dono do negócio..."},
    )
    assert r.status_code == 200
    return r.json()


# --- catálogo ------------------------------------------------------------


def test_catalog_matches_paper_counts():
    cat = get_catalog()
    assert [p["id"] for p in cat["perspectives"]] == ["O", "U", "I", "M", "D"]
    tasks = [t for p in cat["perspectives"] for t in p["tasks"]]
    assert len(tasks) == 28
    assert len(ordered_concern_ids()) == 60
    assert len(set(ordered_concern_ids())) == 60
    per_perspective = {
        p["id"]: sum(len(t["concerns"]) for t in p["tasks"]) for p in cat["perspectives"]
    }
    assert per_perspective == {"O": 10, "U": 9, "I": 11, "M": 14, "D": 16}
    roles = {s["id"] for s in cat["stakeholders"]}
    assert all(set(t["stakeholders"]) <= roles for t in tasks)


def test_catalog_relations_are_valid_and_symmetric():
    known = concerns_by_id()
    for c in known.values():
        assert set(c["related"]) <= set(known), c["id"]
    rel = related_map()
    assert "O10" in rel["M5"] and "M5" in rel["O10"]
    for cid, others in rel.items():
        assert all(cid in rel[o] for o in others)


def test_catalog_merges_miro_template():
    by_id = concerns_by_id()
    assert set(TEMPLATE) <= set(by_id)
    from_template = {cid for cid, c in by_id.items() if c["question_source"] == "template"}
    assert from_template == set(TEMPLATE)
    assert len(from_template) == 47
    assert all(c["questions"] and all(q.strip() for q in c["questions"]) for c in by_id.values())
    assert by_id["O2"]["questions"] == ["Qual é o problema que o ML pretende resolver?"]
    assert len(by_id["U8"]["questions"]) == 2
    assert by_id["D15"]["checklist"] == ["Conjunto de treino", "Conjunto de validação",
                                         "Conjunto de teste"]
    # sem pergunta no template: fica a adaptada, sem exemplo
    assert by_id["M10"]["question_source"] == "adapted"
    assert by_id["M10"]["example"] is None
    assert all(p["goal"] for p in get_catalog()["perspectives"])


def test_catalog_has_no_english_names():
    cat = get_catalog()
    items = cat["stakeholders"] + cat["perspectives"]
    items += [t for p in cat["perspectives"] for t in p["tasks"]]
    items += list(concerns_by_id().values())
    assert not any("name_en" in item for item in items)


def test_catalog_endpoint(auth_client):
    body = auth_client.get("/api/requirements/catalog").json()
    assert body["id"] == "perspecml"
    assert len(body["related"]) == 60


# --- especificações --------------------------------------------------------


def test_create_and_list_spec(auth_client, project, spec):
    assert spec["progress"]["overall"] == {
        "total": 60, "done": 0, "applicable": 0, "not_applicable": 0,
        "specified": 0, "pending": 60,
    }
    assert spec["progress"]["next_concern_id"] == "O1"
    assert spec["concerns"]["O1"]["applicability"] == "pending"
    rows = auth_client.get(f"/api/projects/{project.id}/requirements").json()
    assert [r["title"] for r in rows] == ["Análise de reviews"]


def test_workflow_progress_and_next(auth_client, project, spec):
    base = f"/api/projects/{project.id}/requirements/{spec['id']}/concerns"
    # aplicável sem especificação ainda não conta como concluído
    body = auth_client.put(f"{base}/O1", json={"applicability": "applicable"}).json()
    assert body["concerns"]["O1"]["done"] is False
    assert body["progress"]["next_concern_id"] == "O1"

    body = auth_client.put(
        f"{base}/O1", json={"specification": "Reviews de e-commerce, alto volume diário."}
    ).json()
    assert body["concerns"]["O1"]["done"] is True
    assert body["progress"]["next_concern_id"] == "O2"

    body = auth_client.put(
        f"{base}/O2", json={"applicability": "not_applicable", "notes": "coberto por O1"}
    ).json()
    p = body["progress"]
    assert p["overall"]["done"] == 2
    assert p["perspectives"]["O"] == {
        "total": 10, "done": 2, "applicable": 1, "not_applicable": 1,
        "specified": 1, "pending": 8,
    }
    assert p["tasks"]["O.1"]["done"] == 2
    assert p["next_concern_id"] == "O3"


def test_relation_alert_when_related_is_not_applicable(auth_client, project, spec):
    base = f"/api/projects/{project.id}/requirements/{spec['id']}/concerns"
    auth_client.put(f"{base}/O10", json={"applicability": "applicable"})
    body = auth_client.put(f"{base}/M7", json={"applicability": "not_applicable"}).json()
    assert {"concern_id": "O10", "related_id": "M7"} in body["alerts"]


def test_concern_validation(auth_client, project, spec):
    base = f"/api/projects/{project.id}/requirements/{spec['id']}/concerns"
    assert auth_client.put(f"{base}/X99", json={}).status_code == 404
    assert auth_client.put(f"{base}/O1", json={"applicability": "talvez"}).status_code == 422
    body = auth_client.put(f"{base}/M1", json={"needs_refinement": True}).json()
    assert body["concerns"]["M1"]["needs_refinement"] is True
    assert "priority" not in body["concerns"]["M1"]


def test_update_spec_stakeholders(auth_client, project, spec):
    url = f"/api/projects/{project.id}/requirements/{spec['id']}"
    body = auth_client.patch(url, json={"stakeholders": {"BO": "Ana", "DS": " "}}).json()
    assert body["stakeholders"] == {"BO": "Ana"}
    assert auth_client.patch(url, json={"stakeholders": {"XX": "?"}}).status_code == 422


def test_export_markdown(auth_client, project, spec):
    base = f"/api/projects/{project.id}/requirements/{spec['id']}"
    auth_client.put(f"{base}/concerns/O3", json={"applicability": "applicable",
                                                  "specification": "Classificar reviews."})
    auth_client.put(f"{base}/concerns/U2", json={"applicability": "not_applicable",
                                                  "notes": "Apenas painel."})
    body = auth_client.get(f"{base}/export").json()
    md = body["markdown"]
    assert body["filename"] == "requisitos-analise-de-reviews.md"
    assert "## Perspectiva: Objetivos do sistema (O)" in md
    assert "### M.1 Selecionar e configurar o modelo `E`" in md
    assert "Classificar reviews." in md
    assert "_Não aplicável._ Apenas painel." in md


def test_create_example_spec(auth_client, project):
    r = auth_client.post(f"/api/projects/{project.id}/requirements/example")
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == EXAMPLE_SPEC["title"]
    o = body["progress"]["overall"]
    assert o["specified"] == o["done"] == 47
    assert o["pending"] == 13
    assert body["concerns"]["O3"]["specification"] == "Classificar um cliente como bom ou mau pagador."
    assert body["concerns"]["M10"]["applicability"] == "pending"
    md = auth_client.get(f"/api/projects/{project.id}/requirements/{body['id']}/export").json()
    assert "**Qual é o custo de uma predição errada?**" in md["markdown"]
    assert "miro.com/miroverse/perspecml-machine-learning" in md["markdown"]


def test_other_users_project_is_404(auth_client, db):
    other = User(github_id=2, login="other")
    db.add(other)
    db.flush()
    p = Project(created_by_user_id=other.id, owner="other", repo="x")
    db.add(p)
    db.commit()
    assert auth_client.get(f"/api/projects/{p.id}/requirements").status_code == 404
    assert auth_client.post(f"/api/projects/{p.id}/requirements",
                            json={"title": "t"}).status_code == 404


def test_spec_from_other_project_is_404(auth_client, db, user, project, spec):
    p2 = Project(created_by_user_id=user.id, owner="octocat", repo="outro")
    db.add(p2)
    db.commit()
    assert auth_client.get(f"/api/projects/{p2.id}/requirements/{spec['id']}").status_code == 404


def test_delete_spec_and_project_cascade(auth_client, db, project, spec):
    base = f"/api/projects/{project.id}/requirements/{spec['id']}"
    auth_client.put(f"{base}/concerns/O1", json={"applicability": "applicable"})
    assert auth_client.delete(base).json() == {"ok": True}
    assert db.query(ConcernSpec).count() == 0

    r = auth_client.post(f"/api/projects/{project.id}/requirements", json={"title": "B"}).json()
    auth_client.put(f"/api/projects/{project.id}/requirements/{r['id']}/concerns/D1",
                    json={"applicability": "applicable"})
    assert auth_client.delete(f"/api/projects/{project.id}").json() == {"ok": True}
    assert db.query(RequirementsSpec).count() == 0
    assert db.query(ConcernSpec).count() == 0


# --- login local (dev) -----------------------------------------------------


def test_dev_login_disabled(monkeypatch, client):
    assert Settings.model_fields["dev_login_enabled"].default is False
    monkeypatch.setattr(get_settings(), "dev_login_enabled", False)
    assert client.post("/api/auth/dev-login").status_code == 404
    assert client.get("/api/health").json()["dev_login"] is False


def test_dev_login_refused_with_secure_cookies(monkeypatch, client):
    s = get_settings()
    monkeypatch.setattr(s, "dev_login_enabled", True)
    monkeypatch.setattr(s, "cookie_secure", True)
    assert client.post("/api/auth/dev-login").status_code == 404


def test_dev_login_creates_user_and_demo_project(monkeypatch, client, db):
    monkeypatch.setattr(get_settings(), "dev_login_enabled", True)
    r = client.post("/api/auth/dev-login")
    assert r.status_code == 200
    assert get_settings().session_cookie_name in r.cookies
    me = client.get("/api/auth/me").json()
    assert me["authenticated"] is True and me["login"] == "dev-local"
    # idempotente: não duplica usuário nem projeto demo
    client.post("/api/auth/dev-login")
    assert db.query(User).filter(User.login == "dev-local").count() == 1
    projects = client.get("/api/projects").json()
    assert [p["repo"] for p in projects] == ["demo-ml"]
