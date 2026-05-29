import type { Questionnaire, Stats } from "./types";

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
  const r = await fetch(`${API}/api/stats/${id}`);
  return r.json();
}

export function statsSocketUrl(id: string): string {
  const u = new URL(API);
  const proto = u.protocol === "https:" ? "wss:" : "ws:";
  return `${proto}//${u.host}/ws/stats/${id}`;
}
