import type { SessionView } from "./types";

export type CivicApi = {
  createSession(): Promise<SessionView>;
  sendMessage(id: string, message: string): Promise<SessionView>;
  resolveLocation(id: string, text: string): Promise<SessionView>;
  uploadMedia(id: string, file: File): Promise<SessionView>;
  editField(id: string, field: string, value: unknown): Promise<SessionView>;
  confirm(id: string): Promise<SessionView>;
  reset(id: string): Promise<SessionView>;
};

const base =
  import.meta.env.VITE_API_URL ??
  (import.meta.env.DEV ? "http://localhost:8000" : "");

async function call(path: string, init?: RequestInit): Promise<SessionView> {
  const r = await fetch(base + path, init);
  if (!r.ok) throw new Error("Request failed");
  return r.json();
}

export const api: CivicApi = {
  createSession: () => call("/api/session", { method: "POST" }),
  sendMessage: (id, message) =>
    call(`/api/session/${id}/message`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    }),
  resolveLocation: (id, text) =>
    call(`/api/session/${id}/location/resolve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    }),
  uploadMedia: (id, file) => {
    const body = new FormData();
    body.append("media", file);
    return call(`/api/session/${id}/media`, { method: "POST", body });
  },
  editField: (id, field, value) =>
    call(`/api/session/${id}/fields/${field}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ value }),
    }),
  confirm: (id) =>
    call(`/api/session/${id}/confirm`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ confirmed: true }),
    }),
  reset: (id) => call(`/api/session/${id}/reset`, { method: "POST" }),
};
