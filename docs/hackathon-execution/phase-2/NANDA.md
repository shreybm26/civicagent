# Phase 2 - Nanda Execution

## Objective and distribution

Implement the deterministic workflow and its safety-critical tools. Effort target: **Backend 55%, Frontend 20%, Testing/integration 25%**.

## Owned paths

Own `backend/app/workflow/`, `backend/app/policy/`, `backend/app/tools/location.py`, `backend/app/tools/submit.py`, `backend/app/mock_backend/`, `backend/app/api_entry.py`, `tests/workflow/`, and `tests/location/`. Avoid schema source files, Shrey's router/collection/image modules, frontend manifests, global CSS, and review component internals.

## Execution tasks

- [ ] **N1 (P0, 75 min)** Define typed workflow state and transition functions in `backend/app/workflow/states.py`, `transitions.py`, and `graph.py`; enforce legal transitions and return user message plus state patch.
- [ ] **N2 (P0, 45 min)** Implement `IDLE/IDENTIFYING/COLLECTING/VALIDATING/REVIEWING/SUBMITTING/COMPLETED` nodes and side-path handling for location/media; `SUBMISSION_FAILED` must return to review without data loss.
- [ ] **N3 (P0, 45 min)** Implement `backend/app/tools/location.py` using curated alias normalization, explicit confidence, deterministic zero/multiple-match clarification, and no fabricated address.
- [ ] **N4 (P0, 45 min)** Implement `backend/app/tools/submit.py` and `mock_backend/civic_api.py`; validate required fields and confirmation flag before returning an Open311-style receipt with reference, status, department, timestamp.
- [ ] **N5 (P0, 45 min)** Implement `policy/guardrails.py` and `policy/confirmation.py`: block unsupported claims, invented departments/addresses, PII logging, prompt injection bypass, and auto-submit.
- [ ] **N6 (P0, 60 min)** Replace old `message`/`confirm` behavior in `api_entry.py` with workflow dispatch and route adapters for media/location/edit/confirm/reset; normalize 404/415/413/422/503 errors.
- [ ] **N7 (P1, 30 min)** Add redacted structured logging with session ID/state/event only; never log citizen text, addresses, phone numbers, or photo bytes.
- [ ] **N8 (P0, 60 min)** Test graph transitions, illegal transitions, location aliases/JNTU/vague input, validation, confirmation gate, mock receipt, failure retry, and prompt-injection input.
- [ ] **N9 (P0, 45 min)** Run an API smoke script for the pothole journey using Shrey's service stubs; record latency and fallback behavior.
- [ ] **N10 (P0, 20 min)** Commit and handoff with route examples, test commands, and any deferred provider behavior.

## Frontend contribution

Provide `frontend/src/features/intake/WorkflowNotice.tsx` and typed callbacks for state/message/error/loading rendering only. Do not edit App/global CSS; Shrey integrates the shell.

## Mock/stub requirements

Use `MockRouter`, `MockCollector`, and `MockImageService` fixtures until Shrey's implementations arrive. The graph must run fully with these fixtures and no API key.

## Dependencies, contracts, and execution boundaries

Dependencies: consume Phase 1 `SessionState`/`SessionView` and schema-registry interfaces; Shrey services may remain mocked. API contract: preserve the route shapes in [CONTRACTS.md](../CONTRACTS.md), especially confirmation-gated `POST /confirm` and receipt-only `COMPLETED`. Agent/AI work is N8 provider-failure/prompt-injection handling and N1-N2 state control; LLM output is never authoritative. Backend work is N1-N7; frontend work is the isolated `WorkflowNotice`; integration/testing work is N8-N10. Do not touch schema JSON or frontend manifests.

## Acceptance criteria

Given the happy-path scripted messages and a positive image fixture, the API reaches `REVIEWING`, refuses to confirm until `confirmed=true`, then reaches `COMPLETED` only after a receipt. A second message after completion creates/loads a new service schema without restarting the process.

## Commit boundaries

Suggested commits: `feat(workflow): enforce civic state transitions`; `feat(location): resolve curated Hyderabad aliases`; `feat(submit): add confirmation-gated mock receipt`; `feat(policy): add safety and redaction guards`; `test(workflow): cover critical state and safety paths`; `feat(api): wire deterministic workflow routes`.

## Handoff and Definition of Done

- [ ] N1-N10 complete and tests green.
- [ ] API route examples match `CONTRACTS.md`.
- [ ] No new external service is required for the P0 path.
- [ ] Shrey can integrate review/evidence UI using `SessionView` without changing workflow code.
