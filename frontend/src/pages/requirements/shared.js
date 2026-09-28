// Utilitários compartilhados do módulo de requisitos (PerSpecML).
import { apiFetch } from "../../api/client";

let catalogPromise = null;

// O catálogo é estático: busca uma vez por sessão do navegador.
export function loadCatalog() {
  if (!catalogPromise) {
    catalogPromise = apiFetch("/api/requirements/catalog").catch((e) => {
      catalogPromise = null;
      throw e;
    });
  }
  return catalogPromise;
}

export function indexCatalog(catalog) {
  const concerns = {};
  const tasks = {};
  const perspectives = {};
  const order = [];
  for (const p of catalog.perspectives) {
    perspectives[p.id] = p;
    for (const t of p.tasks) {
      tasks[t.id] = { ...t, perspective: p };
      for (const c of t.concerns) {
        concerns[c.id] = { ...c, task: tasks[t.id], perspective: p };
        order.push(c.id);
      }
    }
  }
  const roles = Object.fromEntries(catalog.stakeholders.map((s) => [s.id, s]));
  return {
    concerns,
    tasks,
    perspectives,
    order,
    roles,
    related: catalog.related,
  };
}

// Estado visual de um concern na especificação.
export function concernState(entry) {
  if (!entry || entry.applicability === "pending") return "pending";
  if (entry.applicability === "not_applicable") return "na";
  return entry.specification?.trim() ? "specified" : "applicable";
}

export const STATE_LABEL = {
  pending: "pendente",
  applicable: "aplicável · falta especificar",
  specified: "especificado",
  na: "não aplicável",
};
