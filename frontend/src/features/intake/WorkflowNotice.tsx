import type { CSSProperties } from "react";

import type { IntakeSessionView } from "./fixtures";

type WorkflowNoticeProps = {
  state: IntakeSessionView["state"];
  message?: string | null;
  error?: { message: string; retryable: boolean } | null;
  loading?: boolean;
  onRetry?: () => void;
};

const stateMessages: Record<IntakeSessionView["state"], string> = {
  IDLE: "Describe a civic issue to begin.",
  IDENTIFYING: "Matching the issue to a supported civic service.",
  COLLECTING: "Collecting the details required by the service schema.",
  LOCATION_REQUIRED: "A recognizable location or landmark is required.",
  MEDIA_ANALYSIS: "Checking whether the image is relevant evidence.",
  VALIDATING: "Validating required fields before review.",
  REVIEWING: "Review the structured request before confirming submission.",
  SUBMITTING: "Submitting the confirmed request to the demo civic backend.",
  SUBMISSION_FAILED: "The request was not completed because no receipt was returned.",
  COMPLETED: "The demo backend returned a receipt for this request.",
};

/** Status-only component; the backend remains the authority for transitions. */
export function WorkflowNotice({ state, message, error, loading = false, onRetry }: WorkflowNoticeProps) {
  const text = loading ? "CivicAgent is working." : error?.message ?? message ?? stateMessages[state];
  const retryVisible = Boolean(error?.retryable && onRetry);

  return (
    <div
      role={error ? "alert" : "status"}
      aria-live={error ? "assertive" : "polite"}
      style={error ? styles.error : styles.notice}
    >
      <span>{text}</span>
      {retryVisible && (
        <button type="button" onClick={onRetry} style={styles.button}>
          Retry
        </button>
      )}
    </div>
  );
}

const styles: Record<string, CSSProperties> = {
  notice: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 12,
    minHeight: 44,
    padding: "10px 12px",
    border: "1px solid #c8d8e5",
    borderRadius: 6,
    background: "#f5f9fc",
    color: "#22313d",
  },
  error: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 12,
    minHeight: 44,
    padding: "10px 12px",
    border: "1px solid #d9b8b8",
    borderRadius: 6,
    background: "#fff7f7",
    color: "#842828",
  },
  button: {
    flex: "0 0 auto",
    padding: "7px 10px",
    border: "1px solid currentColor",
    borderRadius: 6,
    background: "transparent",
    color: "inherit",
    fontWeight: 600,
    cursor: "pointer",
  },
};
