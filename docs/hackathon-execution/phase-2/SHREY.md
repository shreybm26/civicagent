# Phase 2 - Shrey Execution

## Objective and distribution

Implement schema-driven intent, collection, resolution, and image evidence services plus their feature-owned UI pieces. Effort target: **Backend 50%, Frontend 30%, Testing/integration 20%**.

## Owned paths

Own `backend/app/services/router.py`, `backend/app/collection/`, `backend/app/tools/image.py`, schema/data refinements, `frontend/src/features/evidence/`, `frontend/src/features/review/`, `tests/schema/`, and `tests/media/`. Avoid Nanda-owned workflow nodes, policy, location, submit, main/app entrypoints, config, requirements, and global CSS.

## Execution tasks

- [ ] **S1 (P0, 60 min)** Implement `services/router.py` with a constrained prompt/adapter for exactly five service IDs, confidence threshold `<0.7`, ambiguity clarification, and deterministic keyword fallback when provider fails.
- [ ] **S2 (P0, 60 min)** Implement `collection/engine.py` to ask for schema-required fields only, return `Candidate` objects with source/confidence, accept "I don't know" without inventing values, and prohibit policy/legal/deadline answers.
- [ ] **S3 (P0, 60 min)** Implement `collection/resolver.py` with priority `citizen > correction > conversation > photo`, image-only-empty-field rule, conflict clarification, and provenance retention.
- [ ] **S4 (P0, 60 min)** Implement `tools/image.py` provider interface plus deterministic pothole/selfie fixtures: relevant image returns reason and severity candidate; irrelevant image returns rejection reason and no field candidate.
- [ ] **S5 (P1, 30 min)** Add provider timeout/error handling and mock mode; keep live vision optional and bounded by the contract.
- [ ] **S6 (P0, 45 min)** Implement `EvidencePanel.tsx` for upload state, rejected-image message, candidate reason/source, and replace/remove affordances; no direct workflow transitions.
- [ ] **S7 (P0, 45 min)** Implement `ReviewFields.tsx` and `ProvenanceBadge.tsx` to render all schema fields, missing/accepted/candidate states, source labels, and correction callback props.
- [ ] **S8 (P0, 45 min)** Add router/collector/resolver/image tests for all five services, unknown service, missing fields, explicit correction precedence, conflict, positive/negative media, and provider failure.
- [ ] **S9 (P1, 30 min)** Add typed frontend fixtures for `COLLECTING`, `MEDIA_ANALYSIS`, and `REVIEWING`; verify components render without backend implementation.
- [ ] **S10 (P0, 20 min)** Handoff pure-service examples and fixture IDs to Nanda; do not edit shared entrypoints.

## Mock/stub requirements

Every provider is callable with `provider="mock"`. Use deterministic fixtures for JNTU pothole and selfie rejection; live provider output is never trusted as a fact and must pass resolver/validation.

## Dependencies, contracts, and execution boundaries

Dependencies: consume Phase 1 schema and candidate contracts; Nanda can use these services through pure functions before graph wiring exists. API contract: return `RouterResult`, `Candidate[]`, and `ImageResult` exactly as [CONTRACTS.md](../CONTRACTS.md) specifies. Agent/AI work is S1-S5; all provider output remains a candidate. Backend work is S1-S5; frontend work is S6-S7; integration/testing work is S8-S10. Do not edit workflow transitions or route entrypoints.

## Acceptance criteria

Unknown/noise input escalates without a fabricated schema; low-confidence classification clarifies; required fields remain blank until a candidate is accepted by deterministic rules; explicit citizen correction overrides extraction/image; image relevance is visible; all five schemas expose their own required field set.

## Commit boundaries

Suggested commits: `feat(router): constrain service identification`; `feat(collection): add schema-driven candidate engine`; `feat(resolver): enforce provenance priority`; `feat(image): add evidence adapter and fixtures`; `feat(review): render provenance-aware review fields`; `test(services): cover routing collection resolution and media`.

## Handoff and Definition of Done

- [ ] S1-S10 complete and pure-service tests pass.
- [ ] No service name/department is hardcoded outside schemas.
- [ ] Nanda can call each service with a fake state and receive documented output.
- [ ] The Phase 3 UI can use the evidence/review components without changing their contracts.
