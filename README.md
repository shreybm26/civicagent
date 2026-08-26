# CivicAgent

Schema-driven civic issue intake prototype for the Build What Moves India contest.

## Run

```powershell
cd civicagent
py -m pip install -r backend/requirements.txt
$env:PYTHONPATH="backend"
$env:PROVIDER_MODE="mock"
py -m uvicorn app.main:app --reload
```

The default `PROVIDER_MODE=mock` is deterministic and requires no network or API key. Gemini can be configured through `.env` for experiments, but mock mode is the recommended demo path.

Run release checks with `py tools/smoke.py` and `py tools/api_demo.py` while the backend is running. See `docs/demo/release-checklist.md` for the complete rehearsal sequence.

Never commit or expose the Gemini API key in frontend code. Rotate any key posted in chat, logs, screenshots, or a public repository.

All data is synthetic. This is not an official government service and does not submit to a live department.
