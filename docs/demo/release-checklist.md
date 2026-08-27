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

## Final checks

- `/health` returns `status=ok`, `provider=mock`, `schemas=5`, and `tracking_store` of `sqlite` or `supabase`.
- Pothole path reaches `COMPLETED` only after explicit confirmation and a receipt that includes a service request ID plus a one-time access key.
- `POST /api/track` with that ID and key returns the filed status; a wrong key returns `401` and does not leak which value was wrong.
- Track application in the nav opens `/track` without needing the live chat session.
- Selfie upload is rejected without dead-ending the report.
- Prompt injection remains `IDLE` and cannot submit.
- Invalid media returns a safe `415` error; oversized media returns `413`.
- Typed location works when geolocation or map networking is unavailable.
- No real citizen, payment, Aadhaar, PAN, OTP, or government data is used.
