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

Open the frontend through a static server, for example `npx vite --host 127.0.0.1`, then reset before each scenario.

## Final checks

- `/health` returns `status=ok`, `provider=mock`, and `schemas=5`.
- Pothole path reaches `COMPLETED` only after explicit confirmation and a receipt.
- Selfie upload is rejected without dead-ending the report.
- Prompt injection remains `IDLE` and cannot submit.
- Invalid media returns a safe `415` error; oversized media returns `413`.
- Typed location works when geolocation or map networking is unavailable.
- No real citizen, payment, Aadhaar, PAN, OTP, or government data is used.
