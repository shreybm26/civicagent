# Release checklist

## Start

```powershell
cd civicagent
py -m pip install -r backend/requirements.txt
$env:PYTHONPATH="backend"
$env:PROVIDER_MODE="mock"
py -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```powershell
cd civicagent
py tools/smoke.py
py tools/api_demo.py
```

Open the frontend with `cd frontend; npm install; npm run dev`, then reset before each scenario. After a production build (`npm run build` in `frontend`), the API also serves the UI at `http://127.0.0.1:8000/`.

### Seed demonstration dashboard data

Before a pitch or deploy, populate the public city dashboard with Hyderabad demonstration tickets:

```powershell
cd civicagent
$env:PYTHONPATH="backend"
python -m tools.seed_hyderabad_tickets
```

Optional Railway env: `SEED_DEMO_TICKETS=1` auto-seeds on API startup when the store is below the threshold.

Optional pitch helper: `DEMO_STATUS_UPDATES=1` enables `PATCH /api/demo/tickets/{sr_id}/status` so you can advance a live-filed ticket during a demo without exposing controls on the public board.

## Final checks

- `/health` returns `status=ok`, `provider=mock`, `schemas=5`, and `tracking_store` of `sqlite` or `supabase`.
- Pothole path reaches `COMPLETED` only after explicit confirmation and a receipt that includes a service request ID plus a one-time access key.
- Copy sits to the right of the service request ID and access key on the receipt. Email send requires an explicit confirm checkbox.
- `POST /api/track` with that ID and key returns the filed status, a demo timeline, and nearby type counts; a wrong key returns `401` and does not leak which value was wrong.
- `POST /api/track/email` without `confirm_send` returns `422`; a wrong key returns `401`.
- Track application in the nav opens `/track` without needing the live chat session.
- **City dashboard** in the nav opens `/dashboard` and shows ward hotspots, department cards, and a redacted recent-ticket feed (no access keys or citizen PII).
- Run `python -m tools.seed_hyderabad_tickets` (with `PYTHONPATH=backend`) before the demo if the dashboard should look populated.
- Capture a screenshot of the filled dashboard choropleth for the pitch deck.
- Selfie upload is rejected without dead-ending the report.
- Prompt injection remains `IDLE` and cannot submit.
- Invalid media returns a safe `415` error; oversized media returns `413`.
- Typed location works when geolocation or map networking is unavailable.
- No real citizen, payment, Aadhaar, PAN, OTP, or government data is used.
