import { STATE_LABEL, concernState } from "./shared";
import { RoleChips, StateDot } from "./widgets";

const APPLICABILITY = [
  { value: "pending", label: "Pendente" },
  { value: "applicable", label: "Aplicável" },
  { value: "not_applicable", label: "Não aplicável" },
];

// Passos 3–4 do workflow para um concern: verificação de aplicabilidade e,
// se aplicável, especificação guiada pela pergunta do template.
export default function ConcernEditor({
  concern,
  draft,
  setDraft,
  dirty,
  saving,
  idx,
  entries,
  names,
  alerts,
  position,
  onSave,
  onSaveNext,
  onSelect,
}) {
  const task = concern.task;
  const p = concern.perspective;
  const related = idx.related[concern.id] || [];
  const set = (k) => (e) =>
    setDraft((d) => ({
      ...d,
      [k]: e.target.type === "checkbox" ? e.target.checked : e.target.value,
    }));
  const conflicted = alerts
    .filter((a) => a.concern_id === concern.id)
    .map((a) => a.related_id);

  return (
    <div className="req-editor">
      <div className="req-editor-head" style={{ borderColor: p.color }}>
        <div className="req-crumbs">
          <span className="req-persp-tag" style={{ background: p.color }}>
            {p.name} ({p.id})
          </span>
          <span>
            {task.id} {task.name}
          </span>
          {task.experimental && (
            <span
              className="req-exp"
              title="Tarefa com experimentação: os concerns tendem a ser refinados ao longo do projeto."
            >
              E
            </span>
          )}
          <span className="req-hint">
            concern {position.index + 1} de {position.total}
          </span>
        </div>
        <div className="req-goal">{p.goal}</div>
        <div className="req-task-desc">{task.description}</div>
        <div className="req-task-roles">
          Stakeholders da tarefa:{" "}
          <RoleChips ids={task.stakeholders} roles={idx.roles} names={names} />
        </div>
      </div>

      <h2 className="req-concern-title">
        {concern.id} — {concern.name}
      </h2>
      {concern.questions.map((q) => (
        <p key={q} className="req-question">
          {q}
        </p>
      ))}
      {concern.question_source === "adapted" && (
        <p
          className="req-adapted"
          title="O template do Miro não traz pergunta para este concern (incluído na versão final do paper); a pergunta foi adaptada da descrição do concern."
        >
          pergunta adaptada
        </p>
      )}
      {concern.hint && <p className="req-tip">{concern.hint}</p>}
      {concern.checklist.length > 0 && (
        <div className="req-checklist">
          <span>Itens a considerar:</span>
          <ul>
            {concern.checklist.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      )}
      <p className="req-hint">Especificar {concern.description}</p>
      {concern.example && (
        <details className="req-example">
          <summary>Ver exemplo (caso do empréstimo bancário)</summary>
          <div>{concern.example}</div>
        </details>
      )}

      <div
        className="req-segment"
        role="radiogroup"
        aria-label="Aplicabilidade"
      >
        {APPLICABILITY.map((a) => (
          <label
            key={a.value}
            className={`req-seg ${draft.applicability === a.value ? "active " + a.value : ""}`}
          >
            <input
              type="radio"
              name="applicability"
              value={a.value}
              checked={draft.applicability === a.value}
              onChange={set("applicability")}
            />
            {a.label}
          </label>
        ))}
      </div>

      {draft.applicability === "applicable" && (
        <div className="form-group">
          <label htmlFor="req-specification">Especificação</label>
          <textarea
            id="req-specification"
            rows={6}
            value={draft.specification}
            onChange={set("specification")}
            placeholder="Responda à pergunta acima de forma verificável (ex.: “O sistema deve…”)."
          />
        </div>
      )}

      <div className="form-group">
        <label htmlFor="req-notes">
          {draft.applicability === "not_applicable"
            ? "Justificativa (por que não se aplica)"
            : "Notas da discussão (opcional)"}
        </label>
        <textarea
          id="req-notes"
          rows={2}
          value={draft.notes}
          onChange={set("notes")}
        />
      </div>

      <div className="req-meta-row">
        <label title="Marque quando a especificação depende de experimentação e deve ser revisitada.">
          <input
            type="checkbox"
            checked={draft.needs_refinement}
            onChange={set("needs_refinement")}
          />{" "}
          Refinar durante a experimentação
        </label>
      </div>

      <div className="req-actions">
        <button
          type="button"
          className="btn-secondary"
          disabled={!dirty || saving}
          onClick={onSave}
        >
          {saving ? "Salvando…" : dirty ? "Salvar" : "Salvo"}
        </button>
        <button
          type="button"
          className="btn-primary"
          disabled={saving}
          onClick={onSaveNext}
          title="Salva e vai para o próximo concern ainda não concluído, na ordem do workflow"
        >
          Salvar e próximo →
        </button>
      </div>

      {conflicted.length > 0 && (
        <div className="message error">
          Este concern é aplicável, mas está relacionado a{" "}
          {conflicted.map((r) => `${r} ${idx.concerns[r].name}`).join(", ")},
          marcado como não aplicável. Confirme com a equipe se a decisão é
          consistente.
        </div>
      )}

      {related.length > 0 && (
        <div className="req-related">
          <h3>Concerns relacionados</h3>
          <p className="req-hint">
            Relações do diagrama de tarefas e concerns: considere-as para
            identificar trade-offs e dependências.
          </p>
          <ul>
            {related.map((rid) => {
              const rc = idx.concerns[rid];
              const re = entries[rid];
              const st = concernState(re);
              return (
                <li key={rid}>
                  <button
                    type="button"
                    className="req-link"
                    onClick={() => onSelect(rid)}
                  >
                    <StateDot state={st} /> {rid} {rc.name}
                  </button>{" "}
                  <span className="req-hint">
                    {rc.perspective.name} · {STATE_LABEL[st]}
                  </span>
                  {st === "specified" && (
                    <div className="req-related-spec">{re.specification}</div>
                  )}
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}
