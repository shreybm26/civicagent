# CivicAgent Hackathon Execution Plan

This folder is the execution authority for the CivicAgent hackathon build. It is derived from the sole authoritative source, `CivicAgent_Hackathon_Build_Constitution_and_Execution_Blueprint.pdf`, and the repository audit recorded in [AUDIT.md](AUDIT.md).

The plan assumes work begins on 26 August 2026 and the hard submission deadline is **28 August 2026 at 3:00 PM IST**. The PDF header says 4:00 PM IST in one place, but the user-specified deadline is binding; all freeze and rehearsal times below protect 3:00 PM.

## How to use this plan

1. Read [AUDIT.md](AUDIT.md) and [CONTRACTS.md](CONTRACTS.md) before changing code.
2. Work only in the directories assigned to your branch in the active phase.
3. Use the documented contracts and mocks; do not block on another developer's implementation.
4. At each phase deadline, run the phase Definition of Done and merge only through the stated integration owner.
5. Treat P0 work as mandatory. P1 work is completed only after the primary demo path is reliable. P2/P3 work is cut first when time slips.

## Four phases

| Phase | Window (IST) | Milestone |
| --- | --- | --- |
| Phase 1 | 26 Aug, 09:00-13:00 | Stable repository skeleton, contracts, five schemas, and independent mocks |
| Phase 2 | 26 Aug, 13:00 - 27 Aug, 06:00 | Deterministic workflow and all intake capabilities work behind API contracts |
| Phase 3 | 27 Aug, 06:00 - 28 Aug, 09:00 | React demo path works end to end: intake, evidence, review, confirmation, receipt, and schema switch |
| Phase 4 | 28 Aug, 09:00-15:00 | Hardening, freeze, rehearsal, backup path, and final submission |

If the team starts at a different time, preserve the order and the fixed freeze times. Do not move the feature freeze later than 28 Aug 12:00.

## Master execution view

| Phase | Deadline | Nanda | Shrey | Major milestone | Risk |
| --- | --- | --- | --- | --- | --- |
| 1 | 26 Aug 13:00 | Workflow/API contract skeleton; frontend intake seam | Schema registry/router contract; React shell seam | Both branches build against mocks | Contract drift or dependency installation |
| 2 | 27 Aug 06:00 | State graph, location, policy, submit tool, intake UI | Five schemas, collection/resolver, image tool, evidence UI | API can complete scripted pothole path with deterministic fallback | LLM/Chatfield instability; cut to deterministic provider |
| 3 | 28 Aug 09:00 | Integration owner, API wiring, guardrails, intake correction flow | Review/receipt UI, media flow, schema switch, contract tests | Judge-facing React flow is demoable | Merge conflict or CORS/upload issues |
| 4 | 28 Aug 15:00 | Backend hardening, redacted logs, release checklist | UI polish, fixtures, rehearsal evidence, backup client | Frozen, tested, repeatable submission | Late regressions; only P0 fixes after noon |

Feature Freeze: **28 Aug 2026, 12:00 PM IST**

Code Freeze: **28 Aug 2026, 1:00 PM IST**

Full E2E Verification: **28 Aug 2026, 1:00-1:30 PM IST**

Demo Rehearsal: **27 Aug 4:00-6:00 PM** and **28 Aug 1:30-2:00 PM IST**

Emergency Buffer: **28 Aug 2:00-2:45 PM IST**

Final Submission: **28 Aug 2026, 3:00 PM IST**

## Non-negotiable architecture

- One CivicAgent agent, one deterministic state machine. Do not create a multi-agent swarm.
- The schema registry is the authority for required fields, options, departments, and submission metadata.
- The LLM may classify, extract, and suggest; deterministic code validates, resolves conflicts, controls transitions, and gates submission.
- Every derived value carries `{value, source, confidence}`. Citizen answers/corrections always win over extraction or vision candidates.
- Supported service IDs are exactly `road_issue`, `garbage_issue`, `streetlight_issue`, `water_issue`, and `sanitation_issue`.
- Required workflow states are `IDLE`, `IDENTIFYING`, `COLLECTING`, `LOCATION_REQUIRED`, `MEDIA_ANALYSIS`, `VALIDATING`, `REVIEWING`, `SUBMITTING`, `SUBMISSION_FAILED`, and `COMPLETED`.
- No RAG, real government submission, authentication, multilingual/voice pipeline, PDF generation, persistent database, Kubernetes, full A2A, or full MCP implementation in this hackathon build.

## Primary and backup demos

Primary: pothole description -> JNTU Metro location resolution -> relevant pothole image -> provenance-backed severity suggestion -> review/edit -> explicit Submit -> mock receipt -> streetlight schema switch.

Backup: use seeded deterministic provider responses and the API-level client in `tools/demo_client.*` if the LLM, image provider, or browser path fails. The backup must still show state transitions, schema fields, confirmation gate, and a receipt.

## Emergency cut list

If the team is behind schedule, do these things first, in order: remove UI provenance badges while retaining provenance in the review payload; replace live image analysis with an attachment plus deterministic fixture result; accept free-text location with an explicit unverified label; omit the schema-switch scene and demo only the pothole path; use the API-level client if React is unstable.

Never cut the state machine, schema validation, core pothole journey, explicit confirmation, submission receipt, or deterministic safety checks.

