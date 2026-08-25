# Phase 2 - Deterministic Intake Engine

## 1. Phase Objective

Implement the blueprint's trustworthy core: one state-machine workflow, schema-driven collection, constrained service routing, deterministic answer resolution, curated location handling, image candidate/rejection flow, validation, and receipt-gated submission behind the Phase 1 contracts.

## 2. Starting State

Phase 1 contracts, five schemas, location fixtures, task-store seam, and frontend/API mocks are available. No feature is allowed to invent fields or submit without a confirmation flag.

## 3. Ending State

The backend can run all five service schemas through `IDENTIFY -> COLLECT -> LOCATION_REQUIRED/MEDIA_ANALYSIS -> VALIDATING -> REVIEWING -> SUBMITTING -> COMPLETED`, with safe clarification/failure paths. The API can execute the pothole happy path, reject a selfie, clarify a vague location, identify an unknown service, and switch schema after completion using deterministic fixtures when the LLM is unavailable.

## 4. Blueprint Requirements Covered

- LangGraph-style states and transitions: `IDLE`, `IDENTIFYING`, `COLLECTING`, `LOCATION_REQUIRED`, `MEDIA_ANALYSIS`, `VALIDATING`, `REVIEWING`, `SUBMITTING`, `SUBMISSION_FAILED`, `COMPLETED`.
- Service Router constrained to exactly five IDs and `<0.7` clarification threshold with keyword fallback.
- Chatfield collection contract or minimal deterministic collector fallback.
- Answer priority hierarchy and provenance.
- Curated fuzzy location matcher and clarification.
- LLM vision relevance/severity candidate behavior and rejection.
- Deterministic validation, explicit review/confirmation, mock receipt.
- Graceful LLM/input/service errors and no fabricated civic data.

## 5. Current Code Reused

Use Phase 1 task-store, config, schema registry, location dataset, and HTTP contract. The old UUID/receipt concepts remain represented through typed implementations.

## 6. Current Code Modified

Replace the old message/confirm route behavior with workflow dispatch. Keep `/health` and endpoint paths stable while returning the richer `SessionView`. Adapt `.env.example` for mock/live provider selection.

## 7. Current Code Rewritten/Deleted

Delete all remaining keyword-only `process()` logic and inline service field lists. Do not add RAG, multi-agent routing, live GIS, real government calls, or full protocol/auth infrastructure.

## 8. Architecture

`workflow/graph.py` owns transitions and calls domain nodes. `services/router.py` returns only a known service ID or clarification. `collection/engine.py` accepts the schema/current turn/context and returns candidates; the deterministic fallback asks one missing required field at a time. `collection/resolver.py` merges candidates by priority and emits conflicts. `tools/location.py` matches aliases or asks clarification. `tools/image.py` returns relevance/reason/candidates and never overwrites explicit values. `policy/guardrails.py` blocks fabricated departments, policy/legal claims, PII logs, prompt-injection bypass, and unsupported service commitments. `tools/submit.py` checks review validity and confirmation before calling `mock_backend/civic_api.py`, which returns a reference ID. Each node writes a typed state and user-facing message.

## 9. Nanda Work

Own graph/transitions, policy/confirmation, location matcher, submission/mock backend, route integration, error normalization, and workflow/location tests. Build a deterministic provider fallback first; live LLM is an adapter, not a prerequisite.

## 10. Shrey Work

Own all five schema-driven collection behavior, router/provider adapters, candidate/resolver logic, image analysis adapter and fixtures, evidence field view, and schema/media tests. Shrey must expose pure functions that accept and return contract types.

## 11. Parallel Work

Nanda can build graph nodes against fake `RouterResult`, `Candidate[]`, `ImageResult`, `LocationResult`, and submission responses. Shrey can build router/collector/image/resolver against fake graph state and schema fixtures. Integration happens only through the existing adapter interfaces.

## 12. Dependencies

Phase 1 contracts and schemas are prerequisites. Graph integration waits only for interface shapes, not implementations. Live provider calls are optional and must be feature-flagged behind deterministic fallback. The mock submission endpoint must be stable before Phase 3 review UI integration.

## 13. Contracts

Use the exact HTTP, state, candidate, router, image, resolver, and submission contracts in [CONTRACTS.md](../CONTRACTS.md). A node must return a new state plus a message; it may not mutate state in an untracked side channel.

## 14. File Ownership

Nanda: `backend/app/workflow/`, `backend/app/policy/`, `backend/app/tools/location.py`, `backend/app/tools/submit.py`, `backend/app/mock_backend/`, `backend/app/api_entry.py`, `tests/workflow/`, `tests/location/`.

Shrey: `backend/app/services/router.py`, `backend/app/collection/`, `backend/app/tools/image.py`, schema/data refinements, `frontend/src/features/evidence/`, `frontend/src/features/review/`, `tests/schema/`, `tests/media/`.

Nanda remains integration owner for `main.py`, requirements, config, and route registration.

## 15. Merge Strategy

Merge Shrey's pure domain services first. Nanda then wires them into graph nodes and route handlers in one integration commit. If a service is unavailable, retain the interface and use the deterministic fixture; do not redesign shared contracts during merge.

## 16. Testing

Run state transition tests, service routing for road/streetlight/unknown, collection missing-field tests for all five schemas, resolver priority/conflict tests, positive/negative image fixtures, JNTU/vague location tests, validation and no-auto-submit tests, mock receipt tests, prompt-injection test, LLM timeout fallback, and an API-level five-turn pothole smoke test. Check the blueprint latency maximums where practical.

## 17. Risks

Chatfield/LangGraph packages may be unavailable or unstable; use a minimal StateGraph-compatible transition function and deterministic collector fallback, explicitly documented. Vision/provider latency may exceed limits; use seeded image fixtures and a provider timeout. Upload/CORS integration can block Phase 3; test multipart route before UI work.

## 18. Deadline

Phase 2 deadline: **27 Aug 2026, 06:00 AM IST**. Buffer: 90 minutes reserved for provider fallback and state bugs. At 27 Aug 07:30, freeze the deterministic path and cut live integrations that are not stable.

## 19. Definition of Done

- [ ] All required states and transitions are deterministic and tested.
- [ ] All five schemas route and collect without invented fields.
- [ ] Provenance and resolver priority are present in state and review payload.
- [ ] Location match/clarification and image accept/reject paths work.
- [ ] Validation blocks incomplete review and submission.
- [ ] Confirmation flag is mandatory; receipt is mandatory for `COMPLETED`.
- [ ] Unknown service, provider failure, oversized media, invalid choice, and prompt injection fail safely.
- [ ] API-level pothole path completes with a receipt using mocks.

