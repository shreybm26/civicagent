# Phase 2 Nanda Handoff

## Branch and commit scope

Branch: `feat/nanda-workflow-location` (push this branch only; never push these changes directly to `main`).

Phase 2 adds the deterministic backend engine on top of Phase 1:

- `backend/app/workflow/` contains explicit state/event types, legal transition table, five-service mock schema port, and `WorkflowGraph`.
- `backend/app/policy/` contains deterministic guardrails, redacted event payloads, and the explicit confirmation gate.
- `backend/app/tools/location.py` contains 12 curated Hyderabad locations and alias matching with clarification for vague/unknown input.
- `backend/app/tools/submit.py` and `backend/app/mock_backend/civic_api.py` enforce required fields, explicit confirmation, and receipt-gated completion.
- `backend/app/api_entry.py` now owns workflow-backed message, location, media, edit, confirm, reset, and health routes.
- `frontend/src/features/intake/WorkflowNotice.tsx` is an isolated status/error component for Shrey's future shell composition.
- `backend/tests/workflow/` and `backend/tests/location/` cover transitions, guardrails, image fixture behavior, location, correction, failure retry, and schema switching.

## Implemented P0 flow

```text
POST /api/session
  -> POST /message: "There is a huge pothole and a bike almost fell"
  -> POST /location/resolve: {"text":"near JNTU metro"}
  -> POST /media: multipart JPEG/PNG
  -> state REVIEWING with location, photo, and photo-derived severity candidate
  -> PATCH /fields/severity: explicit correction if needed
  -> POST /confirm: {"confirmed":true}
  -> state COMPLETED only after mock receipt
```

Pothole image fixture behavior is deterministic: any non-empty JPEG/PNG is relevant for the road schema unless the filename contains `selfie`, `portrait`, or `face`. A relevant road image proposes `severity=high` with source `photo`; the resolver only fills an empty field. This is intentionally a Phase 2 mock port for Shrey's image provider.

## API behavior

- `GET /health` returns `{status, provider, schemas}` without secrets.
- `POST /api/session` creates an anonymous UUID-backed `IDLE` session.
- `POST /api/session/{id}/message` advances the graph or returns a clarification/escalation without inventing a service.
- `POST /api/session/{id}/location/resolve` uses only curated aliases; no address is fabricated.
- `POST /api/session/{id}/media` accepts bounded JPEG/PNG uploads and returns a graceful irrelevant-image result.
- `PATCH /api/session/{id}/fields/{field_id}` applies a deterministic citizen correction with confidence `1.0`.
- `POST /api/session/{id}/confirm` requires `REVIEWING`, valid required fields, and `{confirmed:true}`. Backend failure returns `SUBMISSION_FAILED`; it never returns `COMPLETED` without a receipt.
- `POST /api/session/{id}/reset` clears the session state while retaining the anonymous session ID.

Errors use `{code,message,retryable}` in `detail` for 404/415/422 and media-size failures. Workflow state is never advanced by the frontend alone.

## Verification

From `backend/`:

```powershell
py -m pip install -r requirements.txt
py -m pytest
py -m uvicorn app.main:app --reload
```

The current machine has no installed Python interpreter, so pytest and the live server could not be run here. `git diff --check` and static ownership/contract inspection were completed. Run the full test suite immediately after installing Python 3.12+ and dependencies.

## Provider and integration handoff

The `WorkflowGraph` owns transitions and deterministic decisions. Shrey can replace the mock schema/router/collector/image behavior through pure ports without editing `workflow/transitions.py`, `policy/`, `tools/location.py`, `tools/submit.py`, or route contracts. Provider output remains a proposal; required-field validation, provenance, confirmation, and receipt rules stay in deterministic code.

The `build_api_router` function retains a `ConversationProvider` injection parameter for the next integration step. The current graph uses the local deterministic fallback so the P0 path has no external dependency.

## Known limitations intentionally deferred

- No LangGraph/Chatfield dependency was added; the workflow is a minimal StateGraph-compatible implementation to preserve the deadline fallback.
- Image analysis is a deterministic fixture adapter, not a live vision call.
- The mock service schemas are a temporary port until Shrey's canonical JSON registry is merged.
- No real government API, GIS, RAG, A2A, MCP, auth, database, or PDF output was added.
