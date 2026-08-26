# Phase 4 - Nanda Execution

## Objective and distribution

Own release reliability and the backend half of final verification. Effort target: **Backend 45%, Frontend 20%, Testing/integration/infrastructure 35%**.

## Owned paths

Own backend runtime/config, release scripts, README, API backup client, safety/latency tests, and final integration notes. Avoid frontend component/style edits except changes explicitly handed off by Shrey.

## Execution tasks

- [ ] **N1 (P0, 45 min, 28 Aug 09:00)** Run clean startup/install/build/health/reset from documented commands; fix only reproducible P0 issues.
- [ ] **N2 (P0, 45 min)** Run API E2E for all five scenarios, prompt injection, LLM timeout, invalid media/location, map-selected coordinate payloads, submission failure/retry, and schema switch; record results.
- [ ] **N3 (P0, 30 min)** Scan logs/output for PII, secrets, addresses, phone patterns, image content, unsafe exceptions, and fabricated department/address values.
- [ ] **N4 (P0, 30 min)** Measure service identification, conversation, image, map/text location resolution, submission, and five-turn latency against blueprint maximums in mock/live modes; lock mock mode if live exceeds limits.
- [ ] **N5 (P1, 45 min)** Add or fix deterministic reset, seeded fixture loading, provider health visibility, and API-level backup client under `tools/`.
- [ ] **N6 (P0, 30 min, by 12:00)** Apply feature freeze: stop new behavior, mark P2/P3 tasks cut, and tag the demo candidate.
- [ ] **N7 (P0, 30 min, by 13:00)** Apply code freeze and merge only tested P0 fixes; run health and smoke checks after each merge.
- [ ] **N8 (P0, 30 min)** Run final E2E and backup client rehearsal with Shrey's frozen UI; verify receipt and schema switch.
- [ ] **N9 (P0, 20 min)** Update README with local run, mock/live provider, reset, scenarios, known limitations, and final architecture map.
- [ ] **N10 (P0, 15 min)** Complete submission package check and final handoff at 2:45 PM; no commands that can mutate the frozen artifact after this point.

## Frontend contribution

Verify CORS, response/error rendering, upload limits, browser-compatible API behavior, map-selected coordinate persistence, typed-location fallback, and that the frontend never bypasses backend confirmation. Report UI defects with exact state/response, not ad hoc fixes in shared files.

## Mock/stub and backup requirements

Keep `PROVIDER_MODE=mock` and seeded pothole/selfie responses as the default. The API backup client must exercise the same `/api/session`, message, media, location, edit, confirm, and reset contracts; it must not call private functions or bypass the confirmation gate. A provider outage is a tested fallback, not a reason to block submission.

## Dependencies, contracts, and execution boundaries

Dependencies: the Phase 3 frozen candidate and its recorded E2E failures, including the locked mapping dependency/version and documented text fallback. API contract: no endpoint or state changes after code freeze except a documented P0 fix; use [CONTRACTS.md](../CONTRACTS.md). Agent/AI work is N2/N4 provider fallback, latency, and prompt-injection verification. Backend work is N1-N5/N7-N10; frontend work is browser verification in the Frontend contribution section; integration/testing work is N2-N4/N8. Do not edit Shrey-owned components or add features after noon.

## Commit boundaries

Suggested commits: `test(release): add final smoke and safety checks`; `fix(runtime): harden startup reset and provider fallback`; `chore(demo): add API backup and seeded fixtures`; `docs(release): finalize runbook and limitations`; `release: freeze civicagent-demo`.

## Acceptance criteria

A clean machine can start the backend/frontend, `/health` is 200, all P0 scenarios are reproducible, logs are safe, mock mode survives provider outage, and the API backup can complete the primary path if the browser fails.

## Handoff and Definition of Done

- [ ] N1-N10 complete with verification evidence.
- [ ] Final release tag/commit is identified.
- [ ] No untested P0 changes remain.
- [ ] Shrey has the exact final run commands and backup instructions.
