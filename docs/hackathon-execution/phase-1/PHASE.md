# Phase 1 - Contracted Foundation

## 1. Phase Objective

Turn the bare prototype into a buildable target structure with one shared contract, five schema sources, deterministic fixtures, and independent frontend/backend seams. This phase removes merge ambiguity before feature work starts.

## 2. Starting State

Only `backend/app/main.py`, `config.py`, `requirements.txt`, one static `frontend/index.html`, and basic environment/README files exist. There is no package manager, test runner, schema registry, workflow, typed state, or media/location fixture.

## 3. Ending State

Both branches build against the same `SessionState`, `SessionView`, candidate, schema, and error contracts. Five schema JSON files and 10-15 curated Hyderabad locations validate at startup. A React dev shell and API client can render mocked session data. `/health`, session creation, reset, and contract-level stubs are runnable without an LLM key.

## 4. Blueprint Requirements Covered

- Six non-negotiable rules are represented as contract invariants.
- Five JSON service schemas and schema-as-authority registry.
- FastAPI + React target architecture and anonymous in-memory task store.
- English-only MVP, local development, mock backend, no RAG/A2A/MCP/auth/database.
- Exact state names and module contracts from Sections 4-7 and Appendix B.

## 5. Current Code Reused

Keep the environment root discovery and dotenv load from `backend/app/config.py`; keep the FastAPI application title/health concept, UUID session idea, receipt shape idea, demo disclaimer, and secret-related `.gitignore` entries.

## 6. Current Code Modified

Adapt `requirements.txt`, `.env.example`, `config.py`, README run instructions, and health response. Move session data out of the untyped `main.py` dictionary behind `contracts.py` and a task-store interface.

## 7. Current Code Rewritten/Deleted

Do not extend `process()` or `snapshot()`; they are replaced by typed stubs. Replace the static inline HTML with a React/Vite shell. Remove the two-service Python dict as an authority; it may remain only as migration reference until Phase 2 schemas land.

## 8. Architecture

The target tree is `backend/app/{contracts.py,main.py,api_entry.py,workflow/,schemas/,services/,collection/,tools/,policy/,data/,mock_backend/}` and `frontend/src/{App.tsx,lib/,features/intake/,features/evidence/,features/review/}`. Phase 1 creates interfaces and fixtures, not the complete workflow. `main.py` owns route registration; feature modules are injected through adapters. JSON schemas are read-only source data. The frontend renders `SessionView` from a typed API client and uses a local mock client when the backend is unavailable. Every error is a typed code/message pair without PII.

## 9. Nanda Work

Own the backend contract/task-store/application seam and a minimal intake feature that renders the mocked state. Nanda is integration owner for Python dependencies, config, entrypoint, CORS, and global runtime behavior.

## 10. Shrey Work

Own the schema registry/data fixtures and the React/tooling seam. Shrey provides typed frontend models/API mock and a feature-owned intake shell that can run against a fixture without touching the backend entrypoint.

## 11. Parallel Work

After `contracts.py` and the TypeScript model are agreed, both branches work independently: Nanda builds FastAPI/task-store stubs; Shrey builds schemas, registry validation, React shell, and mock client. Neither branch needs the other implementation to pass its phase checks.

## 12. Dependencies

The contract baseline must be merged before Phase 1 feature work. Schema registry validation must pass before workflow tasks can consume schemas. Frontend package installation must be confirmed before adding Tailwind; if it exceeds 30 minutes, use a small local CSS module while retaining React.

## 13. Contracts

Use [CONTRACTS.md](../CONTRACTS.md): `SessionState`, `SessionView`, `Candidate`, `RouterResult`, HTTP routes, schema shape, error codes, and shared-file policy. Stubs must return the documented shapes, including null receipt and validation state.

## 14. File Ownership

Nanda: `backend/app/contracts.py` (baseline then additive), `backend/app/main.py`, `backend/app/api_entry.py`, `backend/app/config.py`, `backend/app/store.py`, `frontend/src/features/intake/` fixture consumer, `tests/contracts/`.

Shrey: `backend/app/schemas/`, `backend/app/data/`, `backend/app/services/registry.py`, `frontend/package.json`, lockfile, `frontend/src/lib/`, `frontend/src/App.tsx`, global CSS, `tests/schema/`, `tests/frontend/fixtures/`.

Shared files must not be edited by the non-owner. New dependencies go through the owner, with a message naming package, reason, and fallback.

## 15. Merge Strategy

Merge the contract baseline first. Merge Shrey's package/schema commit, then Nanda's API/store commit, then one integration commit by Nanda for route wiring. Shrey rebases his frontend branch onto that baseline without changing `main.py` or `requirements.txt`.

## 16. Testing

Run schema JSON validation for all five services, contract serialization tests for `SessionView`/`Candidate`, task-store create/get/reset tests, `/health` smoke test, frontend type/build check, and a browser-independent render test against the mock client. Verify no real secret is logged.

## 17. Risks

Dependency installation or unavailable Python/Node can consume the block; use the repository's documented commands and keep a minimal CSS/provider fallback. Contract drift is the highest merge risk; all deviations require an additive versioned field and an update to `CONTRACTS.md`.

## 18. Deadline

Phase 1 deadline: **26 Aug 2026, 1:00 PM IST**. Buffer: 30 minutes for dependency and contract fixes. If not complete by 1:30 PM, freeze the contract and move unimplemented polish to P3.

## 19. Definition of Done

- [ ] Five schema files validate and registry exposes only the five known IDs.
- [ ] `SessionView` and candidate contracts serialize in Python and TypeScript fixtures.
- [ ] `/health`, create-session, and reset stubs run without provider secrets.
- [ ] React shell starts and renders a mocked `IDLE` session.
- [ ] Branch ownership and shared-file rules are recorded in the handoff.
- [ ] No old `process()` path is used by the new route seam.
- [ ] Phase 2 can start without an architecture decision or shared-file edit.

