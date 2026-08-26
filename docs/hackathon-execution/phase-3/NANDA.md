# Phase 3 - Nanda Execution

## Objective and distribution

Own cross-layer backend integration and the intake/location/correction parts of the citizen journey. Effort target: **Backend 40%, Frontend 35%, Testing/integration 25%**.

## Owned paths

Own backend app entrypoints/routes/config, `frontend/src/features/intake/`, `frontend/src/features/location/`, `tests/integration/`, and the primary E2E spec. Avoid `frontend/src/App.tsx`, global CSS, package/lock files, and Shrey's chat/evidence/review/receipt components.

## Execution tasks

- [ ] **N1 (P0, 60 min)** Wire router, collector, resolver, location, image, validation, and submit adapters into graph/API routes; assert every response validates as `SessionView`.
- [ ] **N2 (P0, 45 min)** Verify multipart media, CORS origin, content type/size limits, and safe error responses from a browser-equivalent client.
- [ ] **N3 (P0, 60 min)** Implement `LocationConfirmation.tsx` under `features/location/` with a Leaflet/OpenStreetMap map, clickable and draggable marker, optional browser geolocation, resolved address/coordinates, confidence/source, confirm/clarify behavior, and a typed landmark/text fallback when permissions, tiles, or network are unavailable. Never claim a map-selected address until the backend or approved geocoder returns it.
- [ ] **N4 (P0, 45 min)** Complete intake state UI callbacks for send, retry, reset/new issue, and provider/system error display; preserve backend authority.
- [ ] **N5 (P0, 45 min)** Implement field correction callback flow through `PATCH /fields/{id}` and validate that correction provenance is `1.0` and review is rerun.
- [ ] **N6 (P0, 60 min)** Add integration tests for session -> messages -> map/text location -> media -> review -> edit -> confirm -> receipt and submission failure -> retry, including coordinate payload validation and fallback behavior.
- [ ] **N7 (P0, 60 min)** Create the primary E2E spec for Scenario 1 (map-selected location) and schema-switch Scenario 2 using deterministic mode; capture exact demo steps and expected visible state, plus a text-location fallback check.
- [ ] **N8 (P1, 30 min)** Add prompt-injection and provider-timeout integration cases; confirm state/confirmation cannot be bypassed.
- [ ] **N9 (P1, 30 min)** Update local run/health/troubleshooting instructions after one clean-machine-equivalent run; include demo reset.
- [ ] **N10 (P0, 20 min)** Run rehearsal #1 with Shrey, log only reproducible issues, assign each issue to its owning layer, and freeze contract changes.

## Mock/stub requirements

Keep `PROVIDER_MODE=mock` as the reliable path. E2E must not depend on internet. Use the same endpoint/client flow for mock and live provider modes.

## Dependencies, contracts, and execution boundaries

Dependencies: Phase 2 API smoke path and Shrey's component contracts; fixture mode permits parallel progress. The frontend dependency owner must add Leaflet (and its TypeScript types, or the selected equivalent) through the existing package/lockfile. API contract: browser calls only the endpoints in [CONTRACTS.md](../CONTRACTS.md), and backend remains authoritative for state/validation. Agent/AI work is N1 provider/error integration and N8 prompt-injection/timeout verification. Backend work is N1-N3/N5; frontend work is N3-N5; integration/testing work is N6-N10. Do not edit `App.tsx`, global CSS, or Shrey-owned feature internals.

## Acceptance criteria

The API and browser agree on state after every action, map or text location selections survive validation and review, geolocation/tile failures are recoverable, corrections survive validation, and the primary path reaches a backend receipt. Nanda's frontend code remains isolated under owned feature folders.

## Commit boundaries

Suggested commits: `feat(api): integrate civic workflow services`; `feat(location-ui): add resolved location confirmation`; `feat(intake): add retry reset and correction callbacks`; `test(integration): cover full receipt-gated flow`; `test(e2e): script pothole and schema-switch demo`; `docs(run): record clean demo startup`.

## Handoff and Definition of Done

- [ ] N1-N10 complete and integration/E2E tests recorded.
- [ ] No App/global CSS conflicts introduced.
- [ ] Contract is frozen for Phase 4 except P0 defects.
- [ ] Shrey can compose the final UI without backend edits.
