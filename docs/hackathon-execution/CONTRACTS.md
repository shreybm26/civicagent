# Shared Contracts and Merge Boundaries

These contracts are implementation targets for Phases 1-3. They are deliberately concrete enough for either developer to use a stub without waiting for the other branch.

## Branches and ownership

Use branches `feat/nanda-workflow-location` and `feat/shrey-schema-media`. Both branch from the Phase 1 baseline.

Nanda owns `backend/app/workflow/`, `backend/app/policy/`, `backend/app/tools/location.py`, `backend/app/tools/submit.py`, `backend/app/api_entry.py`, `frontend/src/features/intake/`, `tests/workflow/`, and `tests/location/`.

Shrey owns `backend/app/schemas/`, `backend/app/services/router.py`, `backend/app/collection/`, `backend/app/tools/image.py`, `backend/app/data/`, `frontend/src/features/evidence/`, `frontend/src/features/review/`, `frontend/src/lib/`, `tests/schema/`, and `tests/media/`.

### Shared-file policy

| File or concern | Policy |
| --- | --- |
| `backend/app/main.py` | Nanda is the integration owner. Shrey must not edit it; add routes through Nanda's adapter registration seam. |
| `backend/app/contracts.py` | Pre-Phase 1 baseline, then Nanda owns additive changes. Shrey consumes it and proposes changes in a task note. |
| `backend/requirements.txt`, `backend/app/config.py`, `.env.example` | Nanda is single owner. Shrey requests dependencies/config through the phase handoff. |
| `frontend/package.json`, lockfile, `frontend/src/lib/*` | Shrey is single owner. Nanda consumes typed API helpers and must not edit manifests/global CSS. |
| `frontend/src/App.tsx` and global CSS | Shrey is integration owner. Nanda contributes feature components only under `features/intake/`. |
| README, Docker files, release scripts | Nanda owns runtime docs/scripts; Shrey owns screenshots/demo fixtures under `docs/` or `tools/`. |
| Schema JSON and generated TypeScript types | Shrey owns schema source and generated output. Nanda never edits schema files directly. |

## Session state contract

```json
{
  "session_id": "uuid",
  "state": "IDLE|IDENTIFYING|COLLECTING|LOCATION_REQUIRED|MEDIA_ANALYSIS|VALIDATING|REVIEWING|SUBMITTING|SUBMISSION_FAILED|COMPLETED",
  "service_id": "road_issue|garbage_issue|streetlight_issue|water_issue|sanitation_issue|null",
  "schema_version": "1.0",
  "messages": [{"role":"citizen|agent|system","text":"string","timestamp":"ISO-8601"}],
  "fields": [{"id":"location","value":"string|object|null","source":"citizen|correction|conversation|photo|location|schema","confidence":1.0,"status":"missing|candidate|accepted|rejected"}],
  "evidence": [{"media_id":"string","filename":"string","relevant":true,"reason":"string","candidates":[]}],
  "location": {"query":"string","address":"string","lat":0.0,"lng":0.0,"confidence":0.0,"source":"curated_location|citizen"},
  "validation": {"valid":false,"missing_fields":[],"errors":[]},
  "confirmation": {"confirmed":false,"confirmed_at":null},
  "receipt": null,
  "error": null
}
```

The backend returns a `SessionView` with the same information after every mutating request. The frontend must render only this view; it must not infer workflow transitions locally.

## HTTP API contract

### `GET /health`

Owner: Nanda. Consumer: frontend/demo runner. Returns `{"status":"ok","provider":"mock|llm","schemas":5}`. No secrets or PII.

### `POST /api/session`

Owner: Nanda. Input: none. Output: `SessionView` in `IDLE`. Validation: new anonymous UUID. Errors: `500` only for store failure.

### `POST /api/session/{session_id}/message`

Owner: Nanda integration; router/collector consumers are Shrey modules. Input: `{"message":"string, 1-4000 chars"}`. Output: `SessionView` plus `agent_message`. Deterministic errors: `404` unknown session, `422` empty/oversized text, `503` only when no safe provider fallback exists. Prompt-injection text is treated as citizen content and cannot alter confirmation/state.

### `POST /api/session/{session_id}/media`

Owner: Nanda route seam; Shrey image service. Input: multipart image (`jpg/jpeg/png`, bounded size) and optional caption. Output: `SessionView` with evidence result and any candidate fields. Errors: `415` unsupported type, `413` too large, `404` unknown session, graceful `200` rejection for irrelevant image.

### `POST /api/session/{session_id}/location/resolve`

Owner: Nanda. Input: `{"text":"string"}`. Output: `SessionView` with `location` and a clarification message when zero or multiple curated matches exist. Never fabricate an address.

### `PATCH /api/session/{session_id}/fields/{field_id}`

Owner: Nanda route seam; resolver consumer Shrey. Input: `{"value":"string|choice|object"}`. Output: `SessionView` with source `correction`, confidence `1.0`, and validation rerun. Unknown field/options are `422`.

### `POST /api/session/{session_id}/confirm`

Owner: Nanda. Input: `{"confirmed":true}`. Preconditions: state `REVIEWING`, all required fields valid, explicit `true`. Output: `SessionView` in `COMPLETED` only when mock backend returns a reference ID. Otherwise `SUBMISSION_FAILED` with retryable error. There is no auto-submit path.

### `POST /api/session/{session_id}/reset`

Owner: Nanda. Input: none. Output: fresh `IDLE` session view. Demo reset only; no persistence guarantee.

### Contract examples

These examples are normative fixtures for both branches:

```json
POST /api/session
{}
// 200
{"session_id":"9b2...","state":"IDLE","service_id":null,"fields":[],"validation":{"valid":false,"missing_fields":[]},"confirmation":{"confirmed":false,"confirmed_at":null},"receipt":null,"error":null}
```

```json
POST /api/session/9b2.../message
{"message":"There is a huge pothole near JNTU Metro"}
// 200
{"state":"COLLECTING","service_id":"road_issue","agent_message":"Where exactly is the issue?","fields":[{"id":"description","value":"...","source":"citizen","confidence":1.0,"status":"accepted"}]}
```

```json
POST /api/session/9b2.../confirm
{"confirmed":true}
// 200 only after validation and confirmation gate
{"state":"COMPLETED","receipt":{"reference":"CIV-20260828-1842","status":"Received","department":"Roads & Infrastructure","timestamp":"2026-08-28T08:42:00Z"}}
```

```json
ImageResult
{"relevant":false,"reason":"The image appears to be a selfie, not civic evidence.","candidates":[]}
```

```json
LocationResult
{"query":"near jntu metro","address":"JNTU Metro Station, Kukatpally, Hyderabad 500085","lat":17.4933,"lng":78.3914,"confidence":0.98,"source":"curated_location"}
```

## Candidate and resolver contracts

```python
Candidate = {
  "field_id": str,
  "value": Any,
  "source": Literal["citizen", "correction", "conversation", "photo", "location"],
  "confidence": float,
  "reason": str | None
}

RouterResult = {
  "service_id": str | None,
  "confidence": float,
  "needs_clarification": bool,
  "message": str
}

ImageResult = {
  "relevant": bool,
  "reason": str,
  "candidates": list[Candidate]
}
```

Resolver priority is deterministic: explicit citizen answer, then correction, then conversation extraction, then image inference. Image candidates may fill only empty fields. Conflicting equal-priority values produce a clarification request; code never silently chooses.

## Schema contract

Each of the five JSON files contains `service_id`, `schema_version`, `service_name`, `description`, `department`, `keywords`, `fields`, and `submission`. Required fields are the only fields that can block `REVIEWING`. Departments and endpoint/id-prefix values come from schemas only. The registry validates schema shape at startup and exposes read-only lookup by known ID.

## Merge and handoff protocol

Each commit changes one owned directory and has one purpose. Push after unit tests. At phase checkpoints, Nanda merges Shrey's backend modules first, then Shrey merges Nanda's API contract changes through the integration seams. Never resolve conflicts by editing the other owner's domain files. Shared-file changes require a short note in the phase handoff and one integration commit by the listed owner.
