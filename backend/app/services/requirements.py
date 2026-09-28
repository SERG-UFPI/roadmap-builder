"""Levantamento de requisitos com PerSpecML: progresso, próximo passo e export.

O workflow (Fig. 5 do paper) percorre perspectiva -> tarefa -> concern. Para
cada concern: verificação de aplicabilidade; se aplicável, especificação
guiada pela pergunta do template. Um concern está *concluído* quando foi
marcado como não aplicável ou quando é aplicável e tem especificação.
"""

from __future__ import annotations

import json
import re
import unicodedata

from backend.app.models import ConcernSpec, RequirementsSpec
from backend.app.services.perspecml_catalog import (
    concerns_by_id,
    get_catalog,
    ordered_concern_ids,
    related_map,
)

APPLICABILITY = ("pending", "applicable", "not_applicable")


def is_done(entry: ConcernSpec | None) -> bool:
    if entry is None:
        return False
    if entry.applicability == "not_applicable":
        return True
    return entry.applicability == "applicable" and bool(entry.specification.strip())


def stakeholders(spec: RequirementsSpec) -> dict[str, str]:
    try:
        data = json.loads(spec.stakeholders_json or "{}")
    except json.JSONDecodeError:
        return {}
    return {k: str(v) for k, v in data.items() if isinstance(k, str)}


def concern_dict(entry: ConcernSpec | None, concern_id: str) -> dict:
    if entry is None:
        return {
            "concern_id": concern_id,
            "applicability": "pending",
            "specification": "",
            "notes": "",
            "needs_refinement": False,
            "updated_at": None,
            "done": False,
        }
    return {
        "concern_id": entry.concern_id,
        "applicability": entry.applicability,
        "specification": entry.specification,
        "notes": entry.notes,
        "needs_refinement": entry.needs_refinement,
        "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
        "done": is_done(entry),
    }


def _counts(ids: list[str], entries: dict[str, ConcernSpec]) -> dict:
    c = {"total": len(ids), "done": 0, "applicable": 0, "not_applicable": 0,
         "specified": 0, "pending": 0}
    for cid in ids:
        e = entries.get(cid)
        if e is None or e.applicability == "pending":
            c["pending"] += 1
        elif e.applicability == "not_applicable":
            c["not_applicable"] += 1
        else:
            c["applicable"] += 1
            if e.specification.strip():
                c["specified"] += 1
        if is_done(e):
            c["done"] += 1
    return c


def progress(entries: dict[str, ConcernSpec]) -> dict:
    """Progresso geral, por perspectiva e por tarefa + próximo concern do workflow."""
    per_perspective = {}
    per_task = {}
    for p in get_catalog()["perspectives"]:
        p_ids = []
        for t in p["tasks"]:
            t_ids = [c["id"] for c in t["concerns"]]
            per_task[t["id"]] = _counts(t_ids, entries)
            p_ids += t_ids
        per_perspective[p["id"]] = _counts(p_ids, entries)
    order = ordered_concern_ids()
    next_id = next((cid for cid in order if not is_done(entries.get(cid))), None)
    return {
        "overall": _counts(order, entries),
        "perspectives": per_perspective,
        "tasks": per_task,
        "next_concern_id": next_id,
    }


def relation_alerts(entries: dict[str, ConcernSpec]) -> list[dict]:
    """Relações a revisar: concern aplicável ligado a um concern marcado como não aplicável.

    O paper usa as relações para revelar conflitos e trade-offs; aqui elas viram
    um aviso para a equipe confirmar que a decisão é consistente.
    """
    alerts = []
    rel = related_map()
    for cid in ordered_concern_ids():
        e = entries.get(cid)
        if e is None or e.applicability != "applicable":
            continue
        for other in rel[cid]:
            o = entries.get(other)
            if o is not None and o.applicability == "not_applicable":
                alerts.append({"concern_id": cid, "related_id": other})
    return alerts


def _slug(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text.lower()).strip("-")
    return s[:60] or "especificacao"


def export_markdown(spec: RequirementsSpec, entries: dict[str, ConcernSpec],
                    project_label: str) -> tuple[str, str]:
    """Gera o Perspective-Based ML Specification Template preenchido (Fig. 3)."""
    cat = get_catalog()
    roles = {s["id"]: s for s in cat["stakeholders"]}
    names = stakeholders(spec)
    prog = progress(entries)["overall"]
    by_id = concerns_by_id()

    out: list[str] = []
    out.append(f"# Especificação de requisitos — {spec.title or 'sem título'}")
    out.append("")
    out.append(f"- **Projeto:** {project_label}")
    out.append(f"- **Abordagem:** PerSpecML (catálogo {cat['version']}) — {cat['source']['venue']}, "
               f"doi:{cat['source']['doi']}")
    tpl = cat["template_source"]
    out.append(f"- **Template:** {tpl['title']}, {tpl['authors']} ({tpl['year']}) — {tpl['url']}")
    out.append(f"- **Progresso:** {prog['done']}/{prog['total']} concerns concluídos "
               f"({prog['applicable']} aplicáveis, {prog['not_applicable']} não aplicáveis, "
               f"{prog['pending']} pendentes)")
    out.append("")
    if spec.user_story.strip():
        out.append("## User story")
        out.append("")
        out.extend(f"> {line}" for line in spec.user_story.strip().splitlines())
        out.append("")
    if spec.description.strip():
        out.append("## Descrição adicional de requisitos")
        out.append("")
        out.append(spec.description.strip())
        out.append("")
    if any(v.strip() for v in names.values()):
        out.append("## Stakeholders")
        out.append("")
        for rid, role in roles.items():
            if names.get(rid, "").strip():
                out.append(f"- **{role['name']} ({rid}):** {names[rid].strip()}")
        out.append("")

    for p in cat["perspectives"]:
        out.append(f"## Perspectiva: {p['name']} ({p['id']})")
        out.append("")
        out.append(f"_{p['description']}_")
        out.append("")
        for t in p["tasks"]:
            mark = " `E`" if t["experimental"] else ""
            out.append(f"### {t['id']} {t['name']}{mark}")
            out.append("")
            out.append(f"Stakeholders sugeridos: {', '.join(t['stakeholders'])}")
            out.append("")
            for c in t["concerns"]:
                e = entries.get(c["id"])
                state = e.applicability if e else "pending"
                tag_txt = " (a refinar)" if e and e.needs_refinement else ""
                out.append(f"#### {c['id']} — {c['name']}{tag_txt}")
                out.append("")
                for q in c["questions"]:
                    out.append(f"**{q}**")
                    out.append("")
                if state == "not_applicable":
                    why = e.notes.strip() if e else ""
                    out.append(f"_Não aplicável._{' ' + why if why else ''}")
                elif state == "applicable":
                    out.append(e.specification.strip() or "_(aplicável — especificação pendente)_")
                    if e.notes.strip():
                        out.append("")
                        out.append(f"Notas: {e.notes.strip()}")
                else:
                    out.append("_(pendente de análise)_")
                related = [f"{r} {by_id[r]['name']}" for r in related_map()[c["id"]]]
                if related:
                    out.append("")
                    out.append(f"Relacionados: {', '.join(related)}")
                out.append("")

    filename = f"requisitos-{_slug(spec.title)}.md"
    return filename, "\n".join(out).rstrip() + "\n"
