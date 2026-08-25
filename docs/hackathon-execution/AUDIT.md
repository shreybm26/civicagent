# Repository Audit and Blueprint Gap Analysis

## Audit scope and evidence

Audited on 26 August 2026 from the repository root. The authoritative PDF is the 15-page `CivicAgent_Hackathon_Build_Constitution_and_Execution_Blueprint.pdf` (SHA-256 begins `E0E41115...`). The repository has no `.git` directory, no tests, no frontend package manifest, no Docker files, and no alternate architecture/constitution document.

Current files are limited to:

```text
backend/app/config.py
backend/app/main.py
backend/requirements.txt
frontend/index.html
.env.example
.gitignore
README.md
```

The current backend is a 51-line FastAPI prototype with an in-memory `sessions` dictionary, two hardcoded services (`road_issue`, `streetlight_issue`), a keyword branch, three endpoints (`/health`, `/api/session`, `/api/session/{sid}/message`, `/api/session/{sid}/confirm`), and a mock receipt. It does not run a state graph, load JSON schemas, call an LLM, handle media/location, track provenance, validate candidates, or expose a separate mock civic submission contract.

The current frontend is one minified static HTML file with inline CSS and JavaScript. It calls the backend directly, renders user-controlled text with `innerHTML`, has no image upload, field provenance, location confirmation, review/edit flow, error/loading states, accessible semantics, React build, or reset/demo controls.

The environment could not execute Python during audit because no Python interpreter is installed on the current machine. No implementation was changed, and no runtime behavior was inferred beyond static code inspection.

## Salvage classification

| Current asset | Decision | Reason and required action |
| --- | --- | --- |
| `backend/app/config.py` | KEEP then ADAPT | Environment loading and project-root discovery are useful. Add provider mode, CORS, upload limits, and safe logging settings without exposing secrets. |
| `backend/requirements.txt` | ADAPT | Keep FastAPI/Uvicorn/Pydantic/dotenv baseline; add only the minimum chosen workflow/provider packages. Nanda is the single owner. |
| FastAPI app object/title and `/health` concept in `main.py` | ADAPT | Preserve the health contract and application shell, but move all domain logic into modules. Nanda owns final entrypoint integration. |
| UUID session creation and in-memory store concept | KEEP then ADAPT | Matches anonymous UUID/in-memory MVP. Replace untyped dicts with `SessionState` and bounded reset behavior. |
| Mock receipt/reference concept | KEEP then ADAPT | Matches the constitution's receipt-gated completion. Replace with a validated submission tool and Open311-style mock adapter. |
| Service names and department labels in `SERVICES` | ADAPT | Road/streetlight labels are useful seeds only. Move to five canonical JSON schemas; never keep the dict as authority. |
| `process()` and `snapshot()` | REWRITE | Keyword-only branching, implicit field order, and no explicit states/conflict rules violate the state-machine/schema authority. |
| `frontend/index.html` | REWRITE | Static page is not React and uses unsafe `innerHTML`; replace with feature-owned React components. Preserve only plain-language entry/disclaimer copy. |
| README run instructions/disclaimer | ADAPT | Keep demo-only/no-live-government warning; rewrite commands, architecture, scenarios, reset, and troubleshooting after build. |
| `.env.example` | ADAPT | Keep Gemini placeholders only if the selected provider supports them; add provider mode and never commit secrets. |
| `.gitignore` | KEEP then ADAPT | Preserve secret/cache ignores; add generated assets, uploads, build output, and test artifacts. |
| Any implied LangGraph/Chatfield code | UNKNOWN | No such code exists in the repository. Treat Chatfield as optional behind a provider interface and use deterministic collector fallback if unavailable within 30 minutes. |
| A2A/MCP/auth/RAG/database/PDF/voice/multilingual code | DELETE / NOT APPLICABLE | None exists, and the blueprint explicitly defers these for the MVP. Do not add them. |

## Blueprint-to-codebase gap matrix

| Blueprint requirement | Current implementation | Status | Required action | Phase | Owner |
| --- | --- | --- | --- | --- | --- |
| Six enforceable rules | No enforcement | Not satisfied | Encode state, schema, resolver, provenance, confirmation, receipt invariants and tests | 1-4 | Nanda + Shrey |
| Five canonical service schemas | Two Python dict services | Incompatible | Create five versioned JSON schemas and registry | 1-2 | Shrey |
| Service router against known IDs, confidence threshold/fallback | Keyword `streetlight` else road | Partial/incompatible | Constrained provider + deterministic keyword fallback + unsupported escalation | 2 | Shrey |
| Deterministic workflow states | `idle/collecting/reviewing/completed` strings | Partial/incompatible | Implement explicit graph/transitions and side paths | 2 | Nanda |
| Chatfield collection contract | Hardcoded turns | Not satisfied | Provider interface returning candidates with source/confidence; deterministic fallback | 2 | Shrey |
| Answer priority/conflict resolution | None | Not satisfied | Resolver: citizen/correction > extraction > image; conflict asks citizen | 2 | Shrey |
| Curated 10-15 Hyderabad locations | Free-text stored as-is | Not satisfied | Dataset, alias matcher, confidence and clarification response | 2 | Nanda |
| Image relevance/severity analysis | None | Not satisfied | Upload contract, provider adapter/fixture, candidate-only merge, rejection | 2 | Shrey |
| Provenance `{value, source, confidence}` | Plain values only | Not satisfied | Typed field values and UI/review display | 2-3 | Shrey |
| Review card with edit and Submit | Boolean `review_ready` + confirm endpoint | Partial | Review endpoint/state, edit correction, visible consent, no auto-submit | 3 | Nanda + Shrey |
| Mock civic backend/receipt | Inline fake receipt | Partial | Separate submission service and Open311-style mock response | 2-3 | Nanda |
| Error/unknown/escalation handling | KeyError risk, no errors | Not satisfied | Typed errors, unsupported boundary message, provider fallback | 2-4 | Nanda |
| React chat + field panel + review card | Static HTML/JS | Incompatible | Add React 18/Vite/Tailwind or minimal CSS fallback, component feature ownership | 1-3 | Shrey + Nanda |
| A2A/MCP | None | Not applicable | Explicitly defer; document boundary only | 1 | Nanda |
| Anonymous UUID/in-memory JSON persistence | UUID + dict, no JSON | Partial | Typed task store and optional JSON demo snapshot/reset | 1-2 | Nanda |
| Five scripted scenarios | None | Not satisfied | Seed fixtures and manual/API smoke scripts | 3-4 | Both |
| Safety/privacy/accessibility/auditability | Unsafe `innerHTML`; no logging policy | Not satisfied | Redacted logs, prompt-injection test, disclaimer, semantic UI | 3-4 | Both |
| Local run/deployment/health | Health endpoint only | Partial | Document reproducible local commands, CORS, upload limits, smoke check | 1/4 | Nanda |

## Traceability of the required user journey

Plain-language entry and service identification are implemented in Phase 2 router contracts and Phase 3 ChatPanel integration. Required-field collection and clarification are Phase 2 collection/graph work. Location normalization and confirmation are Phase 2 location work. Photo upload, relevance rejection, severity candidates, and provenance are Phase 2 media work. Validation, review, correction, explicit confirmation, mock submission, and receipt are Phase 2-3. Schema switching after completion is Phase 3. The five manual scenarios, latency/safety checks, deployment, rehearsal, and submission checklist are Phase 4.

## Audit conclusion

This is a thin prototype, not a foundation to extend line by line. The fastest defensible path is a domain rewrite behind a stable contract: preserve the FastAPI/config/session/receipt ideas, isolate the old monolithic logic, and replace the static frontend. No application implementation is being performed as part of this planning task.

