# Phase 1 - Shrey Execution

## Objective and distribution

Create canonical schema/data sources and a React/tooling seam that can consume typed session fixtures. Effort target: **Backend 35%, Frontend 45%, Testing/integration 20%**.

## Owned paths

Own `backend/app/schemas/`, `backend/app/data/`, `backend/app/services/registry.py`, `frontend/package.json`, lockfile, `frontend/src/lib/`, `frontend/src/App.tsx`, global CSS, `tests/schema/`, and `tests/frontend/fixtures/`. Avoid Nanda-owned `main.py`, `api_entry.py`, `config.py`, `store.py`, `backend/app/workflow/`, `backend/app/policy/`, and `frontend/src/features/intake/`.

## Execution tasks

- [ ] **S1 (P0, 60 min)** Create versioned JSON schemas for `road_issue`, `garbage_issue`, `streetlight_issue`, `water_issue`, and `sanitation_issue`; include service metadata, required/optional fields, options, `image_derivable`, submission endpoint, and ID prefix.
- [ ] **S2 (P0, 30 min)** Add 10-15 curated Hyderabad locations with names, area, city, pin, coordinates, and aliases; include JNTU Metro and aliases from the blueprint.
- [ ] **S3 (P0, 45 min)** Implement `backend/app/services/registry.py` to load/validate schemas and reject unknown IDs, missing required properties, invalid field types, or duplicate IDs at startup.
- [ ] **S4 (P0, 30 min)** Add registry tests covering all five IDs, schema shape, options, departments, and an invalid fixture.
- [ ] **S5 (P0, 45 min)** Initialize React 18/Vite package and a typed `frontend/src/lib/types.ts` matching `CONTRACTS.md`; use a local CSS baseline if Tailwind install exceeds 30 minutes.
- [ ] **S6 (P0, 45 min)** Implement `frontend/src/lib/api.ts` with `createSession`, `sendMessage`, `uploadMedia`, `resolveLocation`, `editField`, `confirm`, and `reset` signatures; provide a fixture-backed mock client.
- [ ] **S7 (P1, 45 min)** Wire `App.tsx` to render Nanda's `IntakePanel` through a feature prop and to render a neutral field-panel placeholder from a `SessionView`; do not add domain logic.
- [ ] **S8 (P1, 30 min)** Add accessible global styles, responsive shell, focus states, and demo disclaimer copy without touching intake feature internals.
- [ ] **S9 (P0, 20 min)** Add frontend type/build check and schema fixture test; record package/dependency choices in the handoff.

## Mock/stub requirements

The mock API returns deterministic `IDLE`, `COLLECTING`, `REVIEWING`, and `COMPLETED` fixtures so frontend work can proceed before Nanda's route implementation. It must expose errors with the same `code`, `message`, and `retryable` fields as the backend contract.

## Dependencies, contracts, and execution boundaries

Dependencies: use the Phase 1 contracts and local fixtures; do not wait for Nanda's route implementation. API contract: `frontend/src/lib/api.ts` must implement the operations in [CONTRACTS.md](../CONTRACTS.md) and return typed `SessionView` values. Agent/AI work: schema metadata and provider fixture shapes only; no LLM call is required. Backend work is S1-S4; frontend work is S5-S8; integration/testing work is S9. Keep `App.tsx` and global styles as Shrey-owned integration files.

## Commit boundaries

Suggested commits: `feat(schema): add five canonical civic service schemas`; `feat(data): add curated Hyderabad location fixtures`; `feat(frontend): add React shell and typed mock API`; `test(schema): validate registry and frontend fixtures`.

## Acceptance criteria

`npm run build` (or documented equivalent) succeeds, the shell renders in a clean browser, all five schemas load, and no frontend component reads the old inline `index.html` behavior. The branch is useful with fixtures alone.

## Handoff and Definition of Done

- [ ] S1-S9 complete or deferred with an explicit P2/P3 note.
- [ ] Schema version and field IDs are stable and communicated.
- [ ] Mock API examples match `CONTRACTS.md`.
- [ ] No edits to Nanda-owned entrypoints or domain directories.
- [ ] Phase 2 consumers can import registry, data, and frontend API types directly.
