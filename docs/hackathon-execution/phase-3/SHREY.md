# Phase 3 - Shrey Execution

## Objective and distribution

Own final React composition and the chat, field, evidence, review, receipt, and schema-switch experience. Effort target: **Backend 20%, Frontend 55%, Testing/integration 25%**.

## Owned paths

Own `frontend/src/App.tsx`, `features/chat/`, `features/fields/`, `features/evidence/`, `features/review/`, `features/receipt/`, `frontend/src/lib/`, global CSS, component tests, and demo fixtures. Avoid backend route/config/entrypoint files and Nanda's intake/location feature internals.

## Execution tasks

- [ ] **S1 (P0, 60 min)** Compose `App.tsx` from feature components with one `SessionView` source, API client injection, and clear IDLE/COLLECTING/LOCATION_REQUIRED/REVIEWING/COMPLETED/SUBMISSION_FAILED presentation, including the map picker at the location step.
- [ ] **S2 (P0, 60 min)** Build `ChatPanel` and safe `MessageBubble` components with text input, suggested chips, image action, send/loading/retry states, keyboard/focus behavior, and no `innerHTML`.
- [ ] **S3 (P0, 45 min)** Build `FieldPanel` that shows service name, required/optional status, current value, missing state, and source; keep panel stable while messages change.
- [ ] **S4 (P0, 60 min)** Integrate `EvidencePanel` with real multipart API client, preview/removal, relevant/irrelevant messages, and provenance candidate display.
- [ ] **S5 (P0, 60 min)** Complete `ReviewCard`/`SubmitConfirm`: show all fields, department from schema, edit controls, explicit Submit, disabled/loading/error states, and no auto-submit.
- [ ] **S6 (P0, 45 min)** Build `ReceiptPanel` with reference, status, department, timestamp, demo disclaimer, and `Report another issue` action.
- [ ] **S7 (P0, 45 min)** Implement schema-switch view reset while retaining the completed receipt acknowledgment; verify streetlight fields differ from road fields.
- [ ] **S8 (P1, 45 min)** Add responsive/accessibility polish: visible focus, labels, status announcements, contrast, mobile stacking, usable map controls and marker keyboard/text alternatives, stable upload/input sizes, no overlapping text.
- [ ] **S9 (P0, 60 min)** Add component/interaction tests for all critical states and deterministic API fixtures; test map render/selection/drag, geolocation denial, text fallback, errors, media rejection, correction, submit, receipt, reset, and schema switch.
- [ ] **S10 (P0, 20 min)** Run rehearsal #1 with Nanda, fix only frontend-owned defects, and record remaining P2 polish for Phase 4.

## Backend contribution

Maintain captured contract fixtures and add frontend-side runtime validation/normalization in `frontend/src/lib/` for malformed/failed responses. Do not infer or repair illegal workflow state in UI; surface a safe system error and retry/reset action.

## Mock/stub requirements

Retain a switchable fixture client for every critical state and failure. This is the browser backup path, not a separate product flow.

## Dependencies, contracts, and execution boundaries

Dependencies: Phase 2 components and `SessionView` fixtures; the UI can be completed before live route wiring. Add and lock the Leaflet/OpenStreetMap mapping dependency through the frontend manifest, while keeping typed text location as a no-network fallback. API contract: `frontend/src/lib/api.ts` is the sole caller and follows [CONTRACTS.md](../CONTRACTS.md); UI never creates a receipt or advances state. Agent/AI work is S7 schema-switch rendering and display of router/vision provenance, not provider logic. Backend contribution is S9 malformed-response coverage; frontend work is S1-S8; integration/testing work is S9-S10. Do not edit backend route/config files.

## Acceptance criteria

Judges can understand the current service, fields, provenance, and next action at every turn. The location step supports map pin selection/dragging, clear coordinate/address confirmation, geolocation denial recovery, and typed text fallback. The review and receipt are unambiguous, the page works at demo laptop and mobile widths, and no screen depends on hidden manual state setup.

## Commit boundaries

Suggested commits: `feat(chat): add safe conversational input`; `feat(fields): render live schema progress`; `feat(evidence): integrate image upload and rejection`; `feat(review): add edit and explicit confirmation`; `feat(receipt): show verified submission result`; `test(frontend): cover critical journey states`; `style(frontend): harden responsive accessible layout`.

## Handoff and Definition of Done

- [ ] S1-S10 complete and frontend build/tests pass.
- [ ] Shared frontend files changed only by Shrey.
- [ ] Demo fixture mode is documented and resettable.
- [ ] Nanda's E2E spec passes against the integrated UI.
