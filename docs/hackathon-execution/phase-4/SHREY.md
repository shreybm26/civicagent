# Phase 4 - Shrey Execution

## Objective and distribution

Own final browser reliability, accessibility/readability, demo fixtures, and evidence. Effort target: **Backend 15%, Frontend 55%, Testing/integration 30%**.

## Owned paths

Own frontend components/styles/fixtures, component/browser tests, and `docs/demo/` evidence. Avoid backend runtime/config/requirements/README/release scripts and do not change contracts after freeze without Nanda's integration note.

## Execution tasks

- [ ] **S1 (P0, 45 min, 28 Aug 09:00)** Run the clean-browser primary path five times; fix only reproducible UI defects in owned files.
- [ ] **S2 (P0, 30 min)** Verify Scenario 3 escalation, Scenario 4 selfie rejection, Scenario 5 incomplete water report, and submission failure/retry are understandable and do not dead-end.
- [ ] **S3 (P1, 45 min)** Perform accessibility/readability pass: labels, keyboard flow, focus visibility, live status, contrast, stable layout, mobile width, no clipping/overlap, safe text rendering.
- [ ] **S4 (P0, 30 min)** Verify upload fixtures (pothole and selfie) are present, correctly typed, replaceable, and documented; keep a deterministic fixture fallback.
- [ ] **S5 (P1, 30 min)** Capture screenshots and screen recording of entry, live fields/provenance, location confirmation, image rejection/acceptance, review, receipt, and schema switch under `docs/demo/`.
- [ ] **S6 (P0, 30 min, by 12:00)** Apply feature freeze: stop new UI behavior; cut optional badges/polish if they threaten reliability.
- [ ] **S7 (P0, 30 min, by 13:00)** Run browser rehearsal #2 against the exact frozen candidate and report only P0/P1 regressions with reproduction steps.
- [ ] **S8 (P0, 30 min)** Verify API backup instructions are visually/pitch-ready and the browser can be reset between scenarios.
- [ ] **S9 (P0, 20 min)** Prepare pitch cheat sheet: six rules, opening, architecture proof, wow cues, limitations, and fallback scenario order.
- [ ] **S10 (P0, 15 min)** Sign off the final demo checklist at 2:45 PM and stop editing the release artifact.

## Backend contribution

Use typed API fixtures to test malformed/error responses and verify browser behavior; do not implement backend work in shared files during freeze.

## Mock/stub and backup requirements

Keep fixture-backed `IDLE`, `COLLECTING`, `MEDIA_ANALYSIS`, `REVIEWING`, `SUBMISSION_FAILED`, and `COMPLETED` views available in the frontend client. Browser rehearsal must be repeatable with the deterministic pothole/selfie assets even if the live provider or upload service is unavailable. The fixture client must still show the explicit confirmation and receipt states.

## Dependencies, contracts, and execution boundaries

Dependencies: the Phase 3 frozen UI and Nanda's exact run commands. API contract: consume only the frozen operations in [CONTRACTS.md](../CONTRACTS.md); report contract defects rather than masking them in UI. Agent/AI work is S2 provider/error state presentation and pitch framing of the LLM-proposes/deterministic-decides rule. Backend contribution is fixture-based API/error verification; frontend work is S1-S5/S7-S9; integration/testing work is S1-S2/S6-S8/S10. Do not edit backend runtime or shared contracts during freeze.

## Commit boundaries

Suggested commits: `test(frontend): verify five demo scenarios`; `fix(ui): resolve critical browser states`; `a11y(frontend): harden keyboard and status feedback`; `chore(demo): add media fixtures and screenshots`; `docs(pitch): add rehearsal cheat sheet`.

## Acceptance criteria

The judge-facing browser makes the architecture legible: side panel fills as state changes, provenance is visible where available, review is explicit, receipt is definitive, and schema switch is obvious. The backup path is prepared if visual integration fails.

## Handoff and Definition of Done

- [ ] S1-S10 complete with evidence files and final candidate identifier.
- [ ] No unreviewed UI changes after feature/code freeze.
- [ ] Nanda has exact reproduction steps for any remaining issue.
- [ ] Final screenshots/recording and pitch notes are ready before 2:45 PM.
