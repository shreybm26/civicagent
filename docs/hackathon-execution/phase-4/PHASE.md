# Phase 4 - Freeze, Reliability, and Submission

## 1. Phase Objective

Convert the integrated build into a reliable, defensible hackathon submission with P0/P1 verification, deterministic backup, clean startup/reset, evidence for the pitch, and enough buffer to recover from late failures before 3:00 PM IST.

## 2. Starting State

Phase 3 has a working browser path and API path, with known issues from rehearsal #1. No new architecture or feature is allowed; only fixes and explicitly approved P1 polish remain.

## 3. Ending State

CivicAgent is frozen, starts from a clean environment, passes critical tests and five scenario checks at target reliability, has a primary and backup demo path, has no secret/PII leakage, and is ready for final presentation/submission by 3:00 PM.

## 4. Blueprint Requirements Covered

- Testing/evaluation matrix, latency maximums, safety checks, 15-minute continuous-use scorecard.
- Final pitch checklist: environment, seeded data, backup assets, narrative, final checks.
- Known limitations framing and six enforceable rules.
- Deployment expectations: local server, health check, mock backend, in-memory state.
- All applicable MVP requirements from Sections 3, 8-13 and Appendices A-C.

## 5. Current Code Reused

Use the complete Phase 3 implementation and contract fixtures. Keep mock provider mode, curated locations, mock receipt, local startup, and reset as the stable demo foundation.

## 6. Current Code Modified

Only fix reproducible P0/P1 defects, redact logs, improve loading/error text, verify the frozen map/location fallback behavior, update README/architecture diagram, add release scripts and test fixtures, and prepare screenshots/screen recording/API backup. No new user-facing feature after noon.

## 7. Current Code Rewritten/Deleted

Remove dead prototype path, unused dependencies, stale inline HTML, debug output, accidental secrets, and any demo route that bypasses confirmation. Do not delete the deterministic backup path.

## 8. Architecture

The frozen architecture remains one React client, one FastAPI backend, one deterministic workflow, five JSON schemas, curated location/image fixtures, an interactive Leaflet/OpenStreetMap location picker with typed text fallback, in-memory task store, and mock civic receipt. `PROVIDER_MODE=mock` is the default for rehearsal and may be switched only after a live provider smoke call passes. A single health check and reset script establish a clean run. The API-level demo client mirrors HTTP contracts for browser failure.

## 9. Nanda Work

Own final backend/API hardening, startup/health/reset, P0 defect fixes, redacted logs, provider timeout/fallback verification, safety and latency checks, release checklist, and API backup client.

## 10. Shrey Work

Own final UI polish, accessibility/readability, seeded media fixtures, screenshot/screen recording evidence, pitch visuals, component defect fixes, and browser rehearsal. Shrey must not introduce new UI flows after feature freeze.

## 11. Parallel Work

Nanda runs API/CLI smoke and safety tests while Shrey runs browser/component rehearsal against the frozen contract. Both log reproducible failures by severity and owner. Only P0 fixes block submission; P2 polish is dropped at noon.

## 12. Dependencies

All P0 integration tests and demo startup must pass by 28 Aug 09:00. Feature Freeze at 12:00 prohibits new features. Code Freeze at 13:00 prohibits normal refactors. Final E2E, rehearsal, and backup verification use the exact frozen artifact.

## 13. Contracts

No contract changes after 28 Aug 09:00 except a P0 defect that prevents the demo. Any emergency contract change requires one owner, one integration commit, and rerunning the full E2E path.

## 14. File Ownership

Nanda: backend runtime/config/README/release scripts, API demo client, safety/latency tests, final integration notes.

Shrey: frontend components/styles/fixtures, screenshots/recording notes, browser test evidence, pitch assets under `docs/demo/`.

Shared file policy remains from [CONTRACTS.md](../CONTRACTS.md); no ambiguous edits are permitted during freeze.

## 15. Merge Strategy

Merge only tested commits. Nanda owns the final release branch integration. Shrey submits frontend fixes as isolated commits; Nanda merges and runs the clean-start smoke test. After code freeze, use revertable commits only and do not squash away evidence needed for rollback.

## 16. Testing

Run unit/contract, API integration, component, E2E, five manual scenario checks, map pin selection/drag and coordinate persistence, geolocation permission denial, map-tile/network fallback to typed location, prompt injection, PII-log scan, media/location failure checks, latency sampling, 15-minute continuous-use test, clean-browser test, and API backup path. Record pass/fail with timestamp and build identifier in `docs/demo/verification.md`.

## 17. Risks

Late provider outage, stale browser state, map tile/network outage, geolocation permission differences, upload fixture path, CORS, broken build command, and a last-minute UI regression are the main risks. Default to mock mode, reset before every scenario, keep typed location and the API client as fallbacks, and stop polishing at noon. Do not let a nice-to-have fix consume the emergency buffer.

## 18. Deadline

Phase 4 starts **28 Aug 2026, 09:00 AM IST**. Final polish ends 12:00; feature freeze is 12:00; code freeze is 13:00; E2E/rehearsal is 13:30-14:00; emergency bug buffer is 14:00-14:45; submission package check is 14:45-15:00.

## 19. Definition of Done - Final Hackathon Checklist

- [ ] Required plain-language entry and core user workflow work.
- [ ] React chat, field panel, evidence flow, review card, correction, confirmation, and receipt work.
- [ ] FastAPI health, session, message, media, location, edit, confirm, reset routes work.
- [ ] Agent follows one deterministic workflow; no multi-agent/RAG behavior exists.
- [ ] Five schemas are loaded and authoritative; required/optional fields and departments are correct.
- [ ] Router is constrained to five IDs with safe ambiguity/provider fallback.
- [ ] Collection, resolver, validation, and provenance rules pass tests.
- [ ] Location matching resolves curated aliases and clarifies vague/ambiguous input.
- [ ] The frozen browser path can select and drag a map marker, preserves the selected coordinates through review, and recovers to typed landmark/text location when map tiles or geolocation are unavailable.
- [ ] Relevant image produces candidate evidence; irrelevant image is rejected gracefully.
- [ ] Explicit confirmation is required; no auto-submit path exists.
- [ ] `COMPLETED` is impossible without a mock backend receipt/reference ID.
- [ ] Review/correction and schema-switch flows work without a process restart.
- [ ] Unknown service, provider failure, invalid input, upload failure, location failure, and submission failure are visible and recoverable.
- [ ] No PII or photo content appears in logs; prompt injection cannot bypass state/confirmation.
- [ ] Critical tests, five scenario checks, 15-minute stability check, and latency sampling pass.
- [ ] Clean local startup, `/health`, seeded fixtures, reset, and API backup are verified.
- [ ] Demo disclaimer and known limitations are visible and accurately framed.
- [ ] Screenshots/recording/pitch notes and final submission material are ready by 2:45 PM.
- [ ] No new features or untested changes remain after freeze.
