// Componentes visuais compartilhados do módulo de requisitos.
import { STATE_LABEL } from "./shared";

export function ProgressBar({ counts, color }) {
  const pct = counts.total ? Math.round((counts.done / counts.total) * 100) : 0;
  return (
    <div
      className="req-progress"
      title={`${counts.done}/${counts.total} concluídos · ${counts.applicable} aplicáveis · ${counts.not_applicable} não aplicáveis · ${counts.pending} pendentes`}
    >
      <div
        className="req-progress-fill"
        style={{ width: `${pct}%`, background: color || undefined }}
      />
    </div>
  );
}

export function StateDot({ state }) {
  return (
    <span
      className={`req-dot ${state}`}
      title={STATE_LABEL[state]}
      aria-label={STATE_LABEL[state]}
    />
  );
}

export function RoleChips({ ids, roles, names }) {
  return (
    <span className="req-roles">
      {ids.map((rid) => (
        <span
          key={rid}
          className="req-role"
          title={roles[rid]?.name + (names?.[rid] ? ` — ${names[rid]}` : "")}
        >
          {rid}
          {names?.[rid] ? `: ${names[rid]}` : ""}
        </span>
      ))}
    </span>
  );
}
