# Phase 1 - Nanda Execution

## Objective and distribution

Create the typed FastAPI/task-store seam and the intake feature's API boundary. Effort target: **Backend 55%, Frontend 25%, Testing/integration 20%**.

## Owned paths

Own `backend/app/contracts.py`, `backend/app/main.py`, `backend/app/api_entry.py`, `backend/app/config.py`, `backend/app/store.py`, `frontend/src/features/intake/`, and `tests/contracts/`. Avoid Shrey-owned schema JSON, `backend/app/services/router.py`, `backend/app/collection/`, `backend/app/tools/image.py`, `frontend/package.json`, `frontend/src/App.tsx`, global CSS, and lockfiles.

## Execution tasks

- [ ] **N1 (P0, 45 min)** Create typed Python models for `SessionState`, `SessionView`, `FieldValue`, `Candidate`, `ValidationResult`, `Receipt`, and `CivicError` in `backend/app/contracts.py`; include exact state/service literals from `CONTRACTS.md`.
- [ ] **N2 (P0, 30 min)** Implement `backend/app/store.py` with UUID create/get/reset, bounded in-memory dict, and no PII logging; add missing-session error behavior.
- [ ] **N3 (P0, 45 min)** Adapt `config.py` for provider mode (`mock` default), CORS origin, max upload bytes, and model name; never log secret values.
- [ ] **N4 (P0, 45 min)** Build `api_entry.py` route adapters for `/health`, `POST /api/session`, and `POST /api/session/{id}/reset`; return contract-shaped mocked views.
- [ ] **N5 (P0, 30 min)** Make `main.py` a thin app factory that registers the route adapter and a CORS policy; do not place domain branching in the entrypoint.
- [ ] **N6 (P1, 45 min)** Add `frontend/src/features/intake/IntakePanel.tsx` that renders a mocked `SessionView`, input disabled/loading/error states, and an API boundary prop; do not edit `App.tsx`.
- [ ] **N7 (P0, 30 min)** Add contract and store tests for state literals, null receipt, reset, unknown session, and redacted error strings.
- [ ] **N8 (P1, 20 min)** Prepare a provider stub interface (`class ConversationProvider`) returning `RouterResult`/candidate fixtures for Phase 2; include a deterministic no-key implementation.
- [ ] **N9 (P0, 15 min)** Write a handoff note listing changed files, test commands, dependency requests, and any contract deviations; commit only owned paths.

## Mock/stub requirements

Use a static `IDLE` view and a fake message responder in tests. The mock must never claim a service, location, or receipt unless the fixture explicitly supplies it.

## Dependencies, contracts, and execution boundaries

Dependencies: the Phase 1 contract baseline is the only prerequisite; Shrey's registry may be absent while store/API stubs are built. API contract: implement `GET /health`, `POST /api/session`, and `POST /api/session/{id}/reset` exactly as [CONTRACTS.md](../CONTRACTS.md) specifies. Agent/AI work: define the provider interface and deterministic no-key stub; do not call an LLM in this phase. Backend work is N1-N5/N8; frontend work is N6; integration/testing work is N7/N9. Use `SessionView` fixtures to isolate the frontend.

## Commit boundaries

Suggested commits: `feat(contracts): define civic session and candidate types`; `feat(api): add typed session store and health seam`; `test(contracts): cover state and reset invariants`; `feat(intake): add fixture-driven intake panel`.

## Acceptance criteria

The backend starts with no LLM key, returns 200 from `/health`, creates a UUID session, and resets it. The intake component renders the same fixture shape the eventual API will return. No task requires a Shrey implementation.

## Handoff and Definition of Done

- [ ] N1-N9 complete or explicitly marked P2/P3 with reason.
- [ ] Tests and exact commands recorded.
- [ ] No edits outside Nanda ownership without an integration note.
- [ ] Shrey can consume contracts and mock client without cherry-picking Nanda's domain code.
