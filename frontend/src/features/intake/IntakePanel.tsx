import { useState } from "react";
import type { CSSProperties, FormEvent } from "react";

import { IntakeApi, IntakeField, IntakeSessionView, idleIntakeFixture } from "./fixtures";

type IntakePanelProps = {
  api?: IntakeApi;
  initialSession?: IntakeSessionView;
};

const stateLabels: Record<IntakeSessionView["state"], string> = {
  IDLE: "Ready",
  IDENTIFYING: "Understanding your issue",
  COLLECTING: "Collecting details",
  LOCATION_REQUIRED: "Location needed",
  MEDIA_ANALYSIS: "Reviewing evidence",
  VALIDATING: "Checking details",
  REVIEWING: "Ready for review",
  SUBMITTING: "Submitting",
  SUBMISSION_FAILED: "Submission needs attention",
  COMPLETED: "Complete",
};

function displayValue(field: IntakeField): string {
  if (field.value === null || field.value === undefined || field.value === "") {
    return field.required ? "Needed" : "Not provided";
  }
  return String(field.value);
}

/**
 * Phase 1's isolated intake seam. It owns presentation state only; the API
 * boundary remains injectable so Shrey can compose it without backend code.
 */
export function IntakePanel({ api, initialSession = idleIntakeFixture }: IntakePanelProps) {
  const [session, setSession] = useState<IntakeSessionView>(initialSession);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = message.trim();
    if (!value || busy || !api) return;

    setBusy(true);
    setLocalError(null);
    try {
      const next = await api.sendMessage(value);
      setSession(next);
      setMessage("");
    } catch {
      setLocalError("CivicAgent could not process that message. Try again.");
    } finally {
      setBusy(false);
    }
  }

  async function reset() {
    if (!api || busy) return;
    setBusy(true);
    setLocalError(null);
    try {
      setSession(await api.reset());
      setMessage("");
    } catch {
      setLocalError("CivicAgent could not reset this demo session.");
    } finally {
      setBusy(false);
    }
  }

  const errorMessage = localError ?? session.error?.message ?? null;
  const statusText = busy ? "Working" : stateLabels[session.state];

  return (
    <section aria-labelledby="civicagent-intake-title" style={styles.panel}>
      <header style={styles.header}>
        <div>
          <h2 id="civicagent-intake-title" style={styles.title}>CivicAgent intake</h2>
          <p style={styles.muted}>Phase 1 contract seam</p>
        </div>
        <span role="status" aria-live="polite" style={styles.status}>{statusText}</span>
      </header>

      {session.agent_message && <p role="status" style={styles.message}>{session.agent_message}</p>}
      {errorMessage && <p role="alert" style={styles.error}>{errorMessage}</p>}

      <div style={styles.fields} aria-label="Current structured fields">
        {session.fields.length === 0 ? (
          <p style={styles.muted}>No service selected yet.</p>
        ) : (
          session.fields.map((field) => (
            <div key={field.id} style={styles.field}>
              <span style={styles.fieldLabel}>{field.id}</span>
              <span style={field.status === "missing" ? styles.missing : styles.value}>
                {displayValue(field)}
              </span>
            </div>
          ))
        )}
      </div>

      <form onSubmit={submit} style={styles.form}>
        <label htmlFor="civicagent-message" style={styles.label}>Message</label>
        <div style={styles.controls}>
          <input
            id="civicagent-message"
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="Describe a civic issue"
            disabled={!api || busy}
            maxLength={4000}
            style={styles.input}
          />
          <button type="submit" disabled={!api || busy || !message.trim()} style={styles.button}>
            {busy ? "Working" : "Send"}
          </button>
          <button type="button" onClick={reset} disabled={!api || busy} style={styles.resetButton}>
            Reset
          </button>
        </div>
      </form>
    </section>
  );
}

const styles: Record<string, CSSProperties> = {
  panel: {
    border: "1px solid #d9e1e8",
    borderRadius: 8,
    background: "#ffffff",
    padding: 20,
    color: "#18212b",
    maxWidth: 760,
  },
  header: { display: "flex", justifyContent: "space-between", gap: 16, alignItems: "flex-start" },
  title: { margin: 0, fontSize: 20 },
  muted: { margin: "4px 0 0", color: "#687582", fontSize: 14 },
  status: { color: "#1769aa", fontSize: 14, fontWeight: 600 },
  message: { margin: "20px 0 0", lineHeight: 1.5 },
  error: { margin: "16px 0 0", color: "#9d2c2c", lineHeight: 1.5 },
  fields: { marginTop: 20, borderTop: "1px solid #edf0f2" },
  field: { display: "flex", justifyContent: "space-between", gap: 16, padding: "10px 0", borderBottom: "1px solid #edf0f2" },
  fieldLabel: { fontWeight: 600 },
  value: { color: "#18212b", textAlign: "right" },
  missing: { color: "#687582", textAlign: "right" },
  form: { marginTop: 20 },
  label: { display: "block", fontWeight: 600, marginBottom: 8 },
  controls: { display: "flex", gap: 8, flexWrap: "wrap" },
  input: { flex: "1 1 260px", minWidth: 0, padding: "10px 12px", border: "1px solid #b8c3cc", borderRadius: 6, font: "inherit" },
  button: { padding: "10px 14px", border: 0, borderRadius: 6, background: "#1769aa", color: "#ffffff", fontWeight: 600, cursor: "pointer" },
  resetButton: { padding: "10px 14px", border: "1px solid #b8c3cc", borderRadius: 6, background: "#ffffff", color: "#18212b", fontWeight: 600, cursor: "pointer" },
};
