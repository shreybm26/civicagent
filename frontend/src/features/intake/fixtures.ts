/** Fixture used by Phase 1 while the shared Shrey API client is not present. */

export type IntakeState =
  | "IDLE"
  | "IDENTIFYING"
  | "COLLECTING"
  | "LOCATION_REQUIRED"
  | "MEDIA_ANALYSIS"
  | "VALIDATING"
  | "REVIEWING"
  | "SUBMITTING"
  | "SUBMISSION_FAILED"
  | "COMPLETED";

export type IntakeField = {
  id: string;
  value: unknown;
  required: boolean;
  source?: "citizen" | "correction" | "conversation" | "photo" | "location" | "schema";
  confidence?: number;
  status: "missing" | "candidate" | "accepted" | "rejected";
  reason?: string;
};

export type IntakeSessionView = {
  session_id: string;
  state: IntakeState;
  service_id: string | null;
  schema_version: string;
  fields: IntakeField[];
  agent_message: string | null;
  error: { code: string; message: string; retryable: boolean } | null;
};

export type IntakeApi = {
  sendMessage: (message: string) => Promise<IntakeSessionView>;
  reset: () => Promise<IntakeSessionView>;
};

export const idleIntakeFixture: IntakeSessionView = {
  session_id: "phase-1-fixture",
  state: "IDLE",
  service_id: null,
  schema_version: "1.0",
  fields: [],
  agent_message: null,
  error: null,
};
