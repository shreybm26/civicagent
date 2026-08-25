# CivicAgent

Schema-driven civic issue intake prototype for the Build What Moves India contest.

## Run

```powershell
cd civicagent/backend
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --reload
```

Copy `.env.example` to `.env` and set `GEMINI_API_KEY`. The API currently uses deterministic mock extraction; Gemini will be added behind a provider adapter.

Never commit or expose the Gemini API key in frontend code. Rotate any key posted in chat, logs, screenshots, or a public repository.

All data is synthetic. This is not an official government service and does not submit to a live department.
