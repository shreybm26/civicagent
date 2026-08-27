# CivicAgent

Schema-driven civic issue intake prototype for the [Build What Moves India](https://github.com/shreybm26/civicagent) contest.

## Run locally

```powershell
cd civicagent
py -m pip install -r backend/requirements.txt
$env:PYTHONPATH="backend"
$env:PROVIDER_MODE="mock"
py -m uvicorn app.main:app --reload
```

In another terminal:

```powershell
cd civicagent/frontend
npm install
npm run dev
```

The default `PROVIDER_MODE=mock` is deterministic and requires no network or API key. The assistant still completes the full lodge → location → evidence → review → receipt path using schema keywords and the Hyderabad location directory. Gemini is optional: set `PROVIDER_MODE=gemini` (or `auto`) and `GEMINI_API_KEY` only if you want live model proposals. The workflow still validates, and mock is used if Gemini fails.

The browser UI is a Municipal Civic Cell demonstration portal (tricolor, bilingual chrome, grievance form). It is not an official government website and must not use the State Emblem.

Run release checks with `py tools/smoke.py` and `py tools/api_demo.py` while the backend is running. See `docs/demo/release-checklist.md` for the complete rehearsal sequence.

## Deploy (public URL)

Use **one Railway service** for both the React UI and FastAPI API. That is the right fit for this prototype:

- Sessions are in-memory, so the backend must be a single long-running process (not Vercel serverless).
- Judges get one URL, with no CORS or split-host upload issues.

Do not put the API on Vercel. Vercel functions are stateless; creating a session on one invoke and sending the next message to another would look like the demo is broken.

### Railway

1. Push this repo to GitHub (including `Dockerfile` and `railway.toml`).
2. Open [Railway](https://railway.app), sign in with GitHub, and create a new project from this repository.
3. Railway will build the Docker image (frontend `vite build`, then FastAPI).
4. In Variables, set:

   | Name | Value |
   | --- | --- |
   | `PROVIDER_MODE` | `mock` (use `gemini` plus `GEMINI_API_KEY` only for live-model experiments) |
   | `MAX_SESSIONS` | `100` |

   Leave `VITE_API_URL` unset. Do not add `GEMINI_API_KEY` for the contest demo.
5. Open the service Settings and generate a public domain. Keep replicas at **1**.
6. Confirm `https://YOUR-SERVICE.up.railway.app/health` returns `{"status":"ok","provider":"mock","schemas":5}`, then open the same host in a browser.

After the domain exists, you can optionally set `CORS_ORIGINS` to that exact `https://…` origin. Same-origin traffic does not need it.

### Why not Vercel + Railway?

A split deploy works only if you accept two URLs and extra CORS configuration. If you still want it: host FastAPI on Railway, set `CORS_ORIGINS` to the Vercel origin, build the frontend with `VITE_API_URL` pointing at the Railway API, and give judges the Vercel URL. Same-origin Railway is simpler and safer for the live demo.

Never commit or expose the Gemini API key in frontend code. Rotate any key posted in chat, logs, screenshots, or a public repository.

All data is synthetic. This is not an official government service and does not submit to a live department.
