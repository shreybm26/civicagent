# Phase 3 - Integrated Citizen Journey

## 1. Phase Objective

Join the deterministic backend and feature-owned React components into the complete judge-facing CivicAgent journey: natural entry, live field completion, location confirmation, evidence analysis, review/correction, explicit submission, receipt, and a second-service schema switch.

## 2. Starting State

The backend can complete the scripted paths through contract-level API tests, and React components can render mocked session states independently. Phase 2 P0 behavior is frozen except for integration defects.

## 3. Ending State

A clean browser can execute Scenario 1 end to end and then Scenario 2 without a server restart. Unsupported input, selfie rejection, vague location, incomplete water report, provider failure, and backend failure have usable recovery messages. A deterministic demo mode is available through the same UI and contracts.

## 4. Blueprint Requirements Covered

- UX screens: landing/entry, chat, image input, live field panel, provenance, review card, edit/submit, receipt, errors/escalation.
- Demo scenes 1-7 and scripted scenarios 1-5.
- Explicit citizen confirmation and editable pre-submission state.
- Schema switch proving one engine/five schemas.
- Plain language, disclaimer, accessible controls, loading/error visibility.
- Frontend -> backend -> agent/tools -> structured output -> mock backend integration.

## 5. Current Code Reused

Reuse the Phase 1 React shell/API client and the Phase 2 graph, registry, services, fixtures, and feature components. Preserve endpoint paths and `SessionView`; do not introduce a second client-side state machine.

## 6. Current Code Modified

Wire real API methods into `App.tsx`, replace placeholders with field/evidence/review/receipt features, add correction and reset callbacks, and adapt CORS/upload handling based on real browser behavior. Update README commands only after the integrated path is proven.

## 7. Current Code Rewritten/Deleted

Delete or archive `frontend/index.html` once the React build replaces it. Remove stale mock UI paths that do not use the API client. Remove any route/service shortcut that bypasses workflow validation for the demo.

## 8. Architecture

The browser holds presentation state only: current `SessionView`, input/upload progress, and recoverable UI error. All workflow truth comes from backend responses. `ChatPanel` sends turns, `FieldPanel` renders schema and provenance, `EvidencePanel` uploads images, `LocationConfirmation` displays normalized/clarification state, `ReviewCard` sends corrections, `SubmitConfirm` invokes explicit confirmation, and `ReceiptPanel` renders backend proof. After `COMPLETED`, a new citizen issue invokes the backend's new-issue/schema-switch behavior; the previous receipt remains available as completed history or a compact success message. Mock mode must travel through the same service interfaces and UI.

## 9. Nanda Work

Own backend integration, route/contract correctness, workflow error recovery, location and confirmation UI feature callbacks, correction behavior, CORS/upload limits, and the primary E2E harness. Nanda merges shared backend files.

## 10. Shrey Work

Own `App.tsx` composition, chat/field/evidence/review/receipt visual integration, responsive/accessibility behavior, schema-switch UI, deterministic fixtures, and component/interaction tests. Shrey merges shared frontend files.

## 11. Parallel Work

Nanda runs API integration and builds intake/location/correction callbacks against Shrey's mock client. Shrey builds the full visual journey against Phase 2 fixtures and contract examples. The two streams meet only at `frontend/src/lib/api.ts` and route contracts, each with a single owner.

## 12. Dependencies

Phase 2 API smoke test and stable `SessionView` are required. Review/submit UI may use fixture state until the confirm endpoint is merged. Live provider is never a dependency for UI completion. Schema switch may use a reset/new-issue endpoint contract if post-completion message semantics need isolation.

## 13. Contracts

The frontend sends only documented API operations. It never sets state directly, calculates `review_ready`, marks a candidate accepted, or constructs a receipt. Corrections use `PATCH /fields/{field_id}` and must return source `correction`, confidence `1.0`. Submit is disabled unless backend state is `REVIEWING`, but backend validation remains authoritative.

## 14. File Ownership

Nanda: backend integration entrypoints/routes/config, `frontend/src/features/intake/`, `frontend/src/features/location/`, `tests/integration/`, primary `tests/e2e/` spec.

Shrey: `frontend/src/App.tsx`, `frontend/src/features/chat/`, `features/fields/`, `features/evidence/`, `features/review/`, `features/receipt/`, `frontend/src/lib/`, global CSS, component tests, demo fixtures.

Nanda must not edit App/global CSS. Shrey must not edit backend route registration/config.

## 15. Merge Strategy

First merge backend integration and run the API smoke path. Then Shrey switches the API client from fixtures to real endpoints in one frontend integration commit. Nanda runs the E2E spec against that commit. Fix contract defects in the owning layer; do not add frontend workarounds for invalid backend state or backend UI-specific fields.

## 16. Testing

Run component tests for chat, fields/provenance, media rejection, review/edit, receipt, errors, and reset. Run integration tests for multipart upload, CORS, corrections, confirm gate, submission failure/retry, provider fallback, and schema switch. Run E2E/manual scripts for all five blueprint scenarios, plus prompt injection and a 15-minute continuous-use/reset test. Check text at mobile and desktop widths; P0 correctness wins over optional responsive polish.

## 17. Risks

The largest risk is contract mismatch exposed only in the browser. Capture response fixtures from API tests and use them in component tests. Browser file upload, CORS, or unsafe rendering can cause late failures; exercise them early. Never render citizen/agent strings via `innerHTML`. If live provider output is flaky, lock demo mode to deterministic fixtures before Phase 4.

## 18. Deadline

Functional integration deadline: **27 Aug 2026, 4:00 PM IST** for Demo Rehearsal #1. Hard Phase 3 deadline after fixes: **28 Aug 2026, 9:00 AM IST**. No new workflow architecture after rehearsal; only P0/P1 integration fixes.

## 19. Definition of Done

- [ ] Scenario 1 completes five consecutive runs with receipt and no refresh.
- [ ] Scenario 2 switches to streetlight schema after completion.
- [ ] Scenarios 3-5 have deterministic, understandable outcomes.
- [ ] Location and image states are visible and recoverable.
- [ ] Review shows every required field and provenance; correction works.
- [ ] Submit is explicit and backend-gated; failure does not mark complete.
- [ ] No unsafe HTML rendering, secret exposure, or PII logging.
- [ ] Deterministic demo mode and reset work in the same UI.

