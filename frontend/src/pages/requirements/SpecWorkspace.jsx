import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { apiFetch } from "../../api/client";
import ConcernEditor from "./ConcernEditor";
import { STATE_LABEL, concernState, indexCatalog, loadCatalog } from "./shared";
import { ProgressBar, RoleChips, StateDot } from "./widgets";

const EMPTY_DRAFT = {
  applicability: "pending",
  specification: "",
  notes: "",
  needs_refinement: false,
};

function draftFrom(entry) {
  if (!entry) return EMPTY_DRAFT;
  return {
    applicability: entry.applicability,
    specification: entry.specification || "",
    notes: entry.notes || "",
    needs_refinement: Boolean(entry.needs_refinement),
  };
}

function sameDraft(a, b) {
  return Object.keys(EMPTY_DRAFT).every((k) => a[k] === b[k]);
}

// Próximo concern não concluído depois de `fromId`, na ordem do workflow.
function nextOpen(order, concerns, fromId) {
  const start = order.indexOf(fromId);
  for (let i = 1; i <= order.length; i++) {
    const cid = order[(start + i) % order.length];
    if (!concerns[cid]?.done) return cid;
  }
  return null;
}

function Sidebar({ idx, catalog, spec, currentId, onSelect }) {
  const currentP = idx.concerns[currentId]?.perspective.id;
  const [open, setOpen] = useState({});
  const isOpen = (pid) => open[pid] ?? pid === currentP;
  return (
    <nav className="req-sidebar" aria-label="Perspectivas e tarefas">
      {catalog.perspectives.map((p) => (
        <div key={p.id} className="req-side-persp">
          <button
            type="button"
            className="req-side-head"
            onClick={() => setOpen((o) => ({ ...o, [p.id]: !isOpen(p.id) }))}
            aria-expanded={isOpen(p.id)}
          >
            <span className="req-side-swatch" style={{ background: p.color }} />
            <span className="req-side-name">
              {p.name} ({p.id})
            </span>
            <span className="req-hint">
              {spec.progress.perspectives[p.id].done}/
              {spec.progress.perspectives[p.id].total}
            </span>
          </button>
          <ProgressBar
            counts={spec.progress.perspectives[p.id]}
            color={p.color}
          />
          {isOpen(p.id) &&
            p.tasks.map((t) => (
              <div key={t.id} className="req-side-task">
                <div className="req-side-task-name">
                  {t.name}
                  {t.experimental && <span className="req-exp">E</span>}
                </div>
                {t.concerns.map((c) => (
                  <button
                    type="button"
                    key={c.id}
                    className={`req-side-concern ${c.id === currentId ? "active" : ""}`}
                    onClick={() => onSelect(c.id)}
                  >
                    <StateDot state={concernState(spec.concerns[c.id])} />
                    {c.id} {c.name}
                  </button>
                ))}
              </div>
            ))}
        </div>
      ))}
    </nav>
  );
}

// Visão geral no formato do diagrama de tarefas e concerns (Fig. 2).
function ConcernMap({ catalog, idx, spec, onOpen }) {
  return (
    <div className="req-map">
      <div className="req-legend">
        {Object.entries(STATE_LABEL).map(([k, v]) => (
          <span key={k}>
            <StateDot state={k} /> {v}
          </span>
        ))}
        <span>
          <span className="req-exp">E</span> tarefa com experimentação
        </span>
      </div>
      {spec.alerts.length > 0 && (
        <div className="message error">
          <strong>Relações a revisar:</strong>{" "}
          {spec.alerts
            .map(
              (a) =>
                `${a.concern_id} (aplicável) ↔ ${a.related_id} (não aplicável)`,
            )
            .join(" · ")}
        </div>
      )}
      <div className="req-map-grid">
        {catalog.perspectives.map((p) => (
          <section
            key={p.id}
            className="req-map-persp"
            style={{ borderColor: p.color }}
          >
            <h3 style={{ background: p.color }}>
              {p.name} ({p.id})
              <span>
                {spec.progress.perspectives[p.id].done}/
                {spec.progress.perspectives[p.id].total}
              </span>
            </h3>
            <p className="req-map-goal">{p.goal}</p>
            {p.tasks.map((t) => (
              <div key={t.id} className="req-map-task">
                <div className="req-map-task-head">
                  <RoleChips ids={t.stakeholders} roles={idx.roles} />
                  <span>
                    {t.name}
                    {t.experimental && <span className="req-exp">E</span>}
                  </span>
                </div>
                <div className="req-map-concerns">
                  {t.concerns.map((c) => {
                    const st = concernState(spec.concerns[c.id]);
                    return (
                      <button
                        type="button"
                        key={c.id}
                        className={`req-chip ${st}`}
                        onClick={() => onOpen(c.id)}
                        title={`${c.questions.join("\n")}\n\n${STATE_LABEL[st]}`}
                      >
                        {c.id} {c.name}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </section>
        ))}
      </div>
    </div>
  );
}

// Entrada do processo: funcionalidade (user story) e quem ocupa cada papel.
function SpecContext({ catalog, spec, onSave }) {
  const [form, setForm] = useState({
    title: spec.title,
    user_story: spec.user_story,
    description: spec.description,
    stakeholders: { ...spec.stakeholders },
  });
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));
  const setRole = (rid) => (e) =>
    setForm((f) => ({
      ...f,
      stakeholders: { ...f.stakeholders, [rid]: e.target.value },
    }));

  const save = async (e) => {
    e.preventDefault();
    setBusy(true);
    setMsg("");
    try {
      await onSave(form);
      setMsg("Salvo.");
    } catch (err) {
      setMsg(`Erro: ${err.message}`);
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="req-context" onSubmit={save}>
      <div className="req-context-cols">
        <div>
          <h3>Funcionalidade de ML</h3>
          <div className="form-group">
            <label htmlFor="ctx-title">Título</label>
            <input
              id="ctx-title"
              value={form.title}
              onChange={set("title")}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="ctx-story">User story</label>
            <textarea
              id="ctx-story"
              rows={4}
              value={form.user_story}
              onChange={set("user_story")}
            />
          </div>
          <div className="form-group">
            <label htmlFor="ctx-description">
              Descrição adicional de requisitos
            </label>
            <textarea
              id="ctx-description"
              rows={6}
              value={form.description}
              onChange={set("description")}
            />
          </div>
        </div>
        <div>
          <h3>Stakeholders</h3>
          <p className="req-hint">
            Quem representa cada papel neste levantamento. As tarefas indicam
            quais papéis devem participar da análise.
          </p>
          {catalog.stakeholders.map((s) => (
            <div className="form-group" key={s.id}>
              <label htmlFor={`ctx-role-${s.id}`}>
                {s.id} — {s.name}
              </label>
              <input
                id={`ctx-role-${s.id}`}
                value={form.stakeholders[s.id] || ""}
                onChange={setRole(s.id)}
                placeholder="nomes separados por vírgula"
              />
              <div className="req-hint">{s.description}</div>
            </div>
          ))}
        </div>
      </div>
      <div className="req-actions">
        <button className="btn-primary" disabled={busy}>
          {busy ? "Salvando…" : "Salvar contexto"}
        </button>
        {msg && <span className="req-hint">{msg}</span>}
      </div>

      <h3>Como aplicar (workflow PerSpecML)</h3>
      <ol className="req-workflow">
        {catalog.workflow.map((w) => (
          <li key={w.step}>
            <strong>{w.name}.</strong> {w.description}
          </li>
        ))}
      </ol>
      <p className="req-hint">
        Fonte: {catalog.source.authors}. “{catalog.source.title}”.{" "}
        {catalog.source.venue}.{" "}
        <a
          href={`https://doi.org/${catalog.source.doi}`}
          target="_blank"
          rel="noreferrer"
        >
          doi:{catalog.source.doi}
        </a>
        <br />
        Perguntas, dicas e exemplos: {catalog.template_source.title},{" "}
        {catalog.template_source.authors} ({catalog.template_source.year}).{" "}
        <a href={catalog.template_source.url} target="_blank" rel="noreferrer">
          Miroverse
        </a>
      </p>
    </form>
  );
}

export default function SpecWorkspace() {
  const { id, specId } = useParams();
  const navigate = useNavigate();
  const base = `/api/projects/${id}/requirements/${specId}`;
  const [catalog, setCatalog] = useState(null);
  const [spec, setSpec] = useState(null);
  const [error, setError] = useState("");
  const [view, setView] = useState("guided"); // "guided" | "map" | "context"
  const [currentId, setCurrentId] = useState(null);
  const [draft, setDraft] = useState(EMPTY_DRAFT);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState("");

  const idx = useMemo(
    () => (catalog ? indexCatalog(catalog) : null),
    [catalog],
  );

  const load = useCallback(async () => {
    setError("");
    try {
      const [cat, s] = await Promise.all([loadCatalog(), apiFetch(base)]);
      setCatalog(cat);
      setSpec(s);
      const first =
        s.progress.next_concern_id ||
        cat.perspectives[0].tasks[0].concerns[0].id;
      setCurrentId(first);
      setDraft(draftFrom(s.concerns[first]));
    } catch (e) {
      setError(e.message);
    }
  }, [base]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
  }, [load]);

  const dirty =
    spec && currentId
      ? !sameDraft(draft, draftFrom(spec.concerns[currentId]))
      : false;

  const save = async () => {
    if (!dirty) return spec;
    setSaving(true);
    setToast("");
    try {
      const updated = await apiFetch(`${base}/concerns/${currentId}`, {
        method: "PUT",
        body: draft,
      });
      setSpec(updated);
      return updated;
    } catch (e) {
      setToast(`Erro ao salvar ${currentId}: ${e.message}`);
      return null;
    } finally {
      setSaving(false);
    }
  };

  const select = async (cid) => {
    const s = await save();
    if (!s) return;
    setCurrentId(cid);
    setDraft(draftFrom(s.concerns[cid]));
    setView("guided");
  };

  const saveNext = async () => {
    const s = await save();
    if (!s) return;
    const next = nextOpen(idx.order, s.concerns, currentId);
    if (!next) {
      setToast(
        "Todos os 60 concerns foram analisados. Exporte a especificação.",
      );
      return;
    }
    setCurrentId(next);
    setDraft(draftFrom(s.concerns[next]));
  };

  const saveContext = async (form) => {
    const updated = await apiFetch(base, { method: "PATCH", body: form });
    setSpec(updated);
  };

  const exportMd = async () => {
    const s = await save();
    if (!s) return;
    try {
      const { filename, markdown } = await apiFetch(`${base}/export`);
      const url = URL.createObjectURL(
        new Blob([markdown], { type: "text/markdown;charset=utf-8" }),
      );
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setToast(`Erro ao exportar: ${e.message}`);
    }
  };

  const remove = async () => {
    if (
      !window.confirm(
        `Excluir a especificação “${spec.title}”? Não há como desfazer.`,
      )
    )
      return;
    try {
      await apiFetch(base, { method: "DELETE" });
      navigate(`/projects/${id}?tab=requirements`);
    } catch (e) {
      setToast(`Erro ao excluir: ${e.message}`);
    }
  };

  if (error)
    return (
      <div className="page">
        <div className="message error">{error}</div>
        <Link to={`/projects/${id}?tab=requirements`}>← Voltar</Link>
      </div>
    );
  if (!spec || !idx) return <div className="page-center">Carregando…</div>;

  const o = spec.progress.overall;
  const concern = idx.concerns[currentId];

  return (
    <div className="page req-page">
      <Link to={`/projects/${id}?tab=requirements`} className="btn-text">
        ← Requisitos do projeto
      </Link>
      <div className="req-top">
        <div>
          <h1>{spec.title}</h1>
          {spec.user_story && <p className="req-story">{spec.user_story}</p>}
        </div>
        <div className="req-top-actions">
          <button type="button" className="btn-secondary" onClick={exportMd}>
            Exportar Markdown
          </button>
          <button type="button" className="btn-text" onClick={remove}>
            Excluir
          </button>
        </div>
      </div>
      <div className="req-overall">
        <ProgressBar counts={o} />
        <span className="req-hint">
          {o.done}/{o.total} concluídos · {o.specified} especificados ·{" "}
          {o.not_applicable} não aplicáveis · {o.pending} pendentes
          {o.applicable - o.specified > 0 &&
            ` · ${o.applicable - o.specified} aplicáveis sem especificação`}
        </span>
      </div>

      <div className="issue-tabs" style={{ marginTop: 16 }}>
        {[
          [
            "guided",
            "Análise guiada",
            "Percorre perspectivas → tarefas → concerns (workflow da Fig. 5)",
          ],
          [
            "map",
            "Mapa de concerns",
            "Visão geral no formato do diagrama de tarefas e concerns",
          ],
          [
            "context",
            "Contexto e stakeholders",
            "User story, descrição e quem ocupa cada papel",
          ],
        ].map(([k, label, title]) => (
          <button
            key={k}
            type="button"
            className={`issue-tab ${view === k ? "active" : ""}`}
            onClick={async () => {
              if (k !== "guided" && !(await save())) return;
              setView(k);
            }}
            title={title}
          >
            {label}
            {k === "map" &&
              spec.alerts.length > 0 &&
              ` (${spec.alerts.length}⚠)`}
          </button>
        ))}
      </div>

      {toast && (
        <div
          className={`message ${toast.startsWith("Erro") ? "error" : "success"}`}
        >
          {toast}
        </div>
      )}

      {view === "guided" && (
        <div className="req-guided">
          <Sidebar
            idx={idx}
            catalog={catalog}
            spec={spec}
            currentId={currentId}
            onSelect={select}
          />
          <ConcernEditor
            key={currentId}
            concern={concern}
            draft={draft}
            setDraft={setDraft}
            dirty={dirty}
            saving={saving}
            idx={idx}
            entries={spec.concerns}
            names={spec.stakeholders}
            alerts={spec.alerts}
            position={{
              index: idx.order.indexOf(currentId),
              total: idx.order.length,
            }}
            onSave={save}
            onSaveNext={saveNext}
            onSelect={select}
          />
        </div>
      )}
      {view === "map" && (
        <ConcernMap catalog={catalog} idx={idx} spec={spec} onOpen={select} />
      )}
      {view === "context" && (
        <SpecContext catalog={catalog} spec={spec} onSave={saveContext} />
      )}
    </div>
  );
}
