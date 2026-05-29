import type { Questionnaire, Stats } from "./types";

// In produzione lasciare VITE_API_URL vuoto: API e frontend stanno sullo stesso
// host (reverse proxy nginx) e si usano path relativi, cosi' i cookie di
// sessione ai4auth viaggiano same-origin sulle rotte protette (/api/stats, /ws).
const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function fetchQuestionnaire(id: string): Promise<Questionnaire> {
  const r = await fetch(`${API}/api/questionnaire/${id}`);
  if (!r.ok) throw new Error("questionnaire not found");
  return r.json();
}

export async function submitResponse(payload: {
  questionnaire: string;
  lang: string;
  answers: { question_key: string; value: string | number | boolean | null }[];
}) {
  const r = await fetch(`${API}/api/responses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error("submit failed");
  return r.json();
}

export async function fetchStats(id: string): Promise<Stats> {
  // include = invia il cookie di sessione ai4auth (forward-auth) anche se
  // VITE_API_URL punta a un origin diverso (dev).
  const r = await fetch(`${API}/api/stats/${id}`, { credentials: "include" });
  if (!r.ok) throw new Error(r.status === 403 ? "forbidden" : "stats failed");
  return r.json();
}

export function statsSocketUrl(id: string): string {
  // API vuoto -> same-origin (produzione dietro proxy).
  const base = API || window.location.origin;
  const u = new URL(base, window.location.origin);
  const proto = u.protocol === "https:" ? "wss:" : "ws:";
  return `${proto}//${u.host}/ws/stats/${id}`;
}
