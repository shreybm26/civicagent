# Phase 1 Nanda Handoff

## Branch

`feat/nanda-workflow-location` (local only; do not push to `main`).

## Implemented scope

- Typed Pydantic contracts in `backend/app/contracts.py` for states, sessions, fields, candidates, errors, evidence, location, validation, confirmation, and receipts.
- Bounded thread-safe in-memory store in `backend/app/store.py` with UUID sessions, deep-copy reads, reset, and oldest-session eviction.
- Environment-backed `Settings` in `backend/app/config.py` with mock provider default, CORS origins, upload/session limits, and backward-compatible Gemini names.
- Deterministic no-key provider boundary in `backend/app/provider_stub.py`.
- Thin FastAPI factory in `backend/app/main.py` and route adapters in `backend/app/api_entry.py` for health, create session, safe message seam, and reset.
- Isolated fixture-driven `frontend/src/features/intake/IntakePanel.tsx` and `fixtures.ts`; no `App.tsx`, manifest, global CSS, or Shrey-owned directory changes.
- Contract/store/API tests under `backend/tests/contracts/`.

## Commands

From `backend/`:

```powershell
py -m pip install -r requirements.txt
py -m pytest
py -m uvicorn app.main:app --reload
```

The current environment has no Python interpreter installed, so tests could not be executed here. They are written for Python 3.12+, Pydantic 2, FastAPI, pytest, and httpx.

## Contract notes

- Phase 1 message handling intentionally does not advance workflow state or claim a service. It returns a safe provider clarification through the documented `agent_message` field.
- `SessionView` remains the only API-facing state shape. Later workflow code must replace the adapter behavior without changing field/state literals.
- No Gemini key is read into API responses or logs.
- The frontend component is an isolated seam and expects Shrey's future `frontend/src/lib/api.ts` to satisfy `IntakeApi`.

## Files intentionally not changed

`backend/app/provider.py` (reserved for Shrey's existing provider boundary), schema/router/collection/image paths, `frontend/index.html`, `frontend/package.json`, `frontend/src/App.tsx`, global CSS, README, and lockfiles.
