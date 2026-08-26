# CivicAgent Phase 4 browser verification

Candidate branch: `feat/nanda-phase3-integration`

## Rehearsal checklist

- Start backend with `PROVIDER_MODE=mock` and confirm `/health` returns 200.
- Open the frontend in a clean browser and reset before each scenario.
- Primary path: describe pothole, resolve `near JNTU metro`, upload `pothole.jpg`, review, edit if needed, confirm, verify receipt.
- Fallback path: deny geolocation or disable network; type `Near JNTU Metro, Kukatpally` in the location control.
- Negative path: upload `selfie.jpg`; verify rejection is visible and the report remains editable.
- Safety path: send prompt-injection text; verify no state transition or submission occurs.
- Schema switch: after receipt, start another issue and verify streetlight fields differ.

## Known limitations

The mapping surface is dependency-free and intentionally falls back to typed landmarks. The backend uses synthetic data and a mock receipt; no live government system is contacted. Screenshots and recordings must be captured locally during rehearsal.
