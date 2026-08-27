import type { EmailSentView, SessionView, TrackingView } from "./types";

export type CivicApi = {
  createSession(): Promise<SessionView>;
  sendMessage(id: string, message: string): Promise<SessionView>;
  resolveLocation(id: string, text: string): Promise<SessionView>;
  resolveLocationPin(id: string, input: { lat: number; lng: number; label?: string }): Promise<SessionView>;
  decideImage(id: string, hasImage: boolean): Promise<SessionView>;
  uploadMedia(id: string, file: File): Promise<SessionView>;
  editField(id: string, field: string, value: unknown): Promise<SessionView>;
  confirm(id: string): Promise<SessionView>;
  reset(id: string): Promise<SessionView>;
  track(srId: string, accessKey: string): Promise<TrackingView>;
  sendTrackEmail(srId: string, accessKey: string, email: string, confirmSend: boolean): Promise<EmailSentView>;
};

export class CivicApiError extends Error {
  status: number;
  code?: string;
  constructor(message: string, status: number, code?: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

const base =
  import.meta.env.VITE_API_URL ??
  (import.meta.env.DEV ? "http://localhost:8000" : "");

export function mediaUrl(sessionId: string, mediaId: string): string {
  return `${base}/api/session/${sessionId}/media/${mediaId}`;
}

async function callJson<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(base + path, init);
  if (!r.ok) {
    let message = `Request failed (${r.status})`;
    let code: string | undefined;
    try {
      const body = await r.json();
      const detail = body?.detail;
      if (typeof detail === "string") message = detail;
      else if (detail?.message) message = detail.message;
      if (detail?.code) code = detail.code;
    } catch {
      /* keep generic message */
    }
    throw new CivicApiError(message, r.status, code);
  }
  return r.json();
}

async function call(path: string, init?: RequestInit): Promise<SessionView> {
  return callJson<SessionView>(path, init);
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
  resolveLocationPin: (id, input) =>
    call(`/api/session/${id}/location/resolve`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(input),
    }),
  decideImage: (id, hasImage) =>
    call(`/api/session/${id}/media/decision`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ has_image: hasImage }),
    }),
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
  track: (srId, accessKey) =>
    callJson<TrackingView>("/api/track", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sr_id: srId, access_key: accessKey }),
    }),
  sendTrackEmail: (srId, accessKey, email, confirmSend) =>
    callJson<EmailSentView>("/api/track/email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sr_id: srId,
        access_key: accessKey,
        email,
        confirm_send: confirmSend,
      }),
    }),
};

export function isExpiredSession(error: unknown): boolean {
  return error instanceof CivicApiError && (error.status === 404 || error.code === "SESSION_NOT_FOUND");
}
