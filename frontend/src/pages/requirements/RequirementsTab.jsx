import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiFetch } from "../../api/client";
import { ProgressBar } from "./widgets";

// Aba "Requisitos" do projeto: uma especificação PerSpecML por funcionalidade de ML.
export default function RequirementsTab({ projectId }) {
  const navigate = useNavigate();
  const [specs, setSpecs] = useState(null);
  const [error, setError] = useState("");
  const [showNew, setShowNew] = useState(false);
  const [form, setForm] = useState({
    title: "",
    user_story: "",
    description: "",
  });
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    setError("");
    try {
      setSpecs(await apiFetch(`/api/projects/${projectId}/requirements`));
    } catch (e) {
      setSpecs([]);
      setError(e.message);
    }
  }, [projectId]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
  }, [load]);

  const create = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const spec = await apiFetch(`/api/projects/${projectId}/requirements`, {
        method: "POST",
        body: form,
      });
      navigate(`/projects/${projectId}/requirements/${spec.id}`);
    } catch (e) {
      setError(e.message);
      setBusy(false);
    }
  };

  const createExample = async () => {
    setBusy(true);
    setError("");
    try {
      const spec = await apiFetch(
        `/api/projects/${projectId}/requirements/example`,
        { method: "POST" },
      );
      navigate(`/projects/${projectId}/requirements/${spec.id}`);
    } catch (e) {
      setError(e.message);
      setBusy(false);
    }
  };

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  return (
    <div className="req-tab">
      <div className="phase-head">
        <h2>Levantamento de requisitos</h2>
        <div className="home-actions">
          <button
            type="button"
            className="btn-primary"
            onClick={() => setShowNew((v) => !v)}
          >
            ＋ Nova especificação
          </button>
          <button
            type="button"
            className="btn-secondary"
            disabled={busy}
            onClick={createExample}
            title="Cria uma especificação preenchida com o exemplo do template PerSpecML, para conhecer o método"
          >
            Criar a partir do exemplo (empréstimo bancário)
          </button>
        </div>
      </div>
      <p className="req-hint">
        Baseado no <strong>PerSpecML</strong> (Villamizar et al., JSS 2024):
        cada funcionalidade de ML é analisada em 5 perspectivas — objetivos do
        sistema, experiência do usuário, infraestrutura, modelo e dados — por
        meio de 28 tarefas e 60 concerns, envolvendo os stakeholders de cada
        tarefa.
      </p>

      {showNew && (
        <form className="req-new" onSubmit={create}>
          <div className="form-group">
            <label htmlFor="new-title">Funcionalidade de ML</label>
            <input
              id="new-title"
              value={form.title}
              onChange={set("title")}
              placeholder="ex.: Análise de sentimento de reviews"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="new-story">User story</label>
            <textarea
              id="new-story"
              rows={3}
              value={form.user_story}
              onChange={set("user_story")}
              placeholder="Como <papel>, quero <objetivo>, para que <benefício>."
            />
          </div>
          <div className="form-group">
            <label htmlFor="new-description">
              Descrição adicional de requisitos (opcional)
            </label>
            <textarea
              id="new-description"
              rows={3}
              value={form.description}
              onChange={set("description")}
              placeholder="Critérios de aceitação, restrições conhecidas…"
            />
          </div>
          <button className="btn-primary" disabled={busy}>
            {busy ? "Criando…" : "Criar e iniciar análise"}
          </button>
        </form>
      )}

      {error && <div className="message error">{error}</div>}

      {specs === null ? (
        <p className="req-hint">Carregando…</p>
      ) : specs.length === 0 ? (
        <p className="req-hint">
          Nenhuma especificação ainda. Crie uma a partir da user story da
          funcionalidade de ML.
        </p>
      ) : (
        <div className="phase-list">
          {specs.map((s) => {
            const o = s.progress.overall;
            return (
              <Link
                key={s.id}
                to={`/projects/${projectId}/requirements/${s.id}`}
                className="req-spec-row"
              >
                <div>
                  <div className="phase-title">{s.title}</div>
                  <div className="req-hint">
                    {o.applicable} aplicáveis · {o.not_applicable} não
                    aplicáveis · {o.pending} pendentes · atualizado{" "}
                    {new Date(s.updated_at).toLocaleString()}
                  </div>
                </div>
                <ProgressBar counts={o} />
                <div className="phase-counts">
                  {o.done}/{o.total} concerns
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
