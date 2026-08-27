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

The default `PROVIDER_MODE=mock` is deterministic and requires no network or API key. The assistant still completes the full lodge → location → evidence → review → receipt path using schema keywords and the Hyderabad location directory. After a successful submit you get a **service request ID** and a one-time **access key**. Use **Track application** (`/track`) to look that request up later. Gemini is optional: set `PROVIDER_MODE=gemini` (or `auto`) and `GEMINI_API_KEY` only if you want live model proposals. The workflow still validates, and mock is used if Gemini fails.

The browser UI is a Municipal Civic Cell demonstration portal (tricolor, bilingual chrome, grievance form). It is not an official government website and must not use the State Emblem.

Live chat sessions stay in memory (they reset when Railway restarts). Submitted grievances are stored so they can be tracked: SQLite on your laptop, Supabase in production.

Run release checks with `py tools/smoke.py` and `py tools/api_demo.py` while the backend is running. See `docs/demo/release-checklist.md` for the complete rehearsal sequence.

## Track a grievance (Supabase)

You need a database for tracking. In-memory storage cannot survive a Railway restart, so a submitted SR ID would vanish. Local development uses SQLite automatically (`backend/data/civicagent-grievances.db`). For the public demo, use Supabase so tracking records live outside the Railway container.

Do these steps once:

1. Open [https://supabase.com](https://supabase.com), sign in, and click **New project**.
2. Name it something like `civicagent`, pick a region close to India (Mumbai / `ap-south-1` if listed), set a strong database password, and wait until the project is `Active`.
3. In the left sidebar open **SQL Editor** → **New query**. Paste the contents of `backend/sql/grievances.sql` and click **Run**. That creates `public.grievances` and turns on Row Level Security with **no policies**, so the public `anon` key cannot read or write rows.
4. Open **Project Settings** (gear) → **API**. Copy:
   - **Project URL** → this is `SUPABASE_URL` (example: `https://abcdxyz.supabase.co`)
   - **service_role** key (click **Reveal**) → this is `SUPABASE_SERVICE_ROLE_KEY`
5. Do **not** put the `anon` `public` key in Railway, and never put `service_role` in frontend code, `VITE_*` variables, GitHub, or chat. The FastAPI backend is the only process that should hold it; it bypasses RLS on purpose.
6. Generate a pepper used to hash access keys (this is not the login key shown to the citizen):

   ```powershell
   py -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

   Copy the output as `TRACKING_PEPPER`. If you change this later, previously issued access keys will stop working.
7. In Railway → your service → **Variables**, add:

   | Name | Value |
   | --- | --- |
   | `SUPABASE_URL` | the Project URL from step 4 |
   | `SUPABASE_SERVICE_ROLE_KEY` | the `service_role` secret from step 4 |
   | `TRACKING_PEPPER` | the random string from step 6 |

   Keep `PROVIDER_MODE=mock` and `MAX_SESSIONS=100`. Leave `VITE_API_URL` unset.
8. Railway will redeploy. Confirm `https://YOUR-SERVICE.up.railway.app/health` includes `"tracking_store":"supabase"`. Then lodge a demo grievance, copy the SR ID and access key from the acknowledgement, open **Track application**, and look it up.

If those three variables are missing, the API falls back to SQLite inside the container. That file is lost on every Railway restart, so tracking will look broken in production until Supabase is configured.

The access key is shown **once** on the receipt. Only a SHA-256 HMAC of it is stored (`key_hash`). The chat transcript and photo bytes are not written to this table.

The track page also shows a **demonstration neighbourhood picture**: counts by issue type, synthetic nearby samples labelled as demo (not live ULB data), plus other tickets filed in this prototype within about 2 km. The timeline stops at “awaiting ward assignment” on purpose.

## Email the acknowledgement

After submit, citizens can email themselves the service request ID, access key, and tracking link. The API will not send until they tick confirm — a typo would leak the key. This is demonstration mail, not a department notice.

**Use Gmail SMTP if anyone besides you needs to receive the mail** (teammates, judges). Resend's `onboarding@resend.dev` test sender can only deliver to the Resend account owner.

1. In Google Account → Security, turn on 2-Step Verification, then create an [App password](https://myaccount.google.com/apppasswords) for Mail. Do **not** use your normal Gmail password.
2. In Railway → Variables, add:

   | Name | Value |
   | --- | --- |
   | `SMTP_USERNAME` | your Gmail address |
   | `SMTP_PASSWORD` | the 16-character app password |
   | `SMTP_FROM` | `CivicAgent Demo <your-gmail@gmail.com>` |
   | `SMTP_HOST` | `smtp.gmail.com` (optional; this is the default) |
   | `SMTP_PORT` | `587` (optional; this is the default) |
   | `PUBLIC_BASE_URL` | your Railway `https://…` URL (optional if the request host is already that URL) |

3. Confirm `/health` includes `"mail_configured": true` and `"mail_backend":"smtp"`. Lodge a grievance and send a test to someone else's inbox.

Resend remains optional. If only `RESEND_API_KEY` is set with `onboarding@resend.dev`, mail still works for the account owner and tracking still works for everyone else.

Without SMTP or Resend, tracking still works; send returns a clear “not configured” error.

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
   | `SUPABASE_URL` | your Supabase project URL (see **Track a grievance** above) |
   | `SUPABASE_SERVICE_ROLE_KEY` | Supabase `service_role` secret (backend only) |
   | `TRACKING_PEPPER` | random string used to hash access keys |
   | `SMTP_USERNAME` | Gmail address used to send acknowledgements to any inbox |
   | `SMTP_PASSWORD` | Gmail app password (not the account password) |
   | `SMTP_FROM` | `CivicAgent Demo <your-gmail@gmail.com>` |
   | `PUBLIC_BASE_URL` | public `https://…` URL for links in the email (optional) |

   Leave `VITE_API_URL` unset. Do not add `GEMINI_API_KEY` for the contest demo. Never add `SUPABASE_SERVICE_ROLE_KEY` to the frontend.
5. Open the service Settings and generate a public domain. Keep replicas at **1**.
6. Confirm `https://YOUR-SERVICE.up.railway.app/health` returns `status=ok`, `provider=mock`, `schemas=5`, and `tracking_store=supabase`, then open the same host in a browser.

After the domain exists, you can optionally set `CORS_ORIGINS` to that exact `https://…` origin. Same-origin traffic does not need it.

### Why not Vercel + Railway?

A split deploy works only if you accept two URLs and extra CORS configuration. If you still want it: host FastAPI on Railway, set `CORS_ORIGINS` to the Vercel origin, build the frontend with `VITE_API_URL` pointing at the Railway API, and give judges the Vercel URL. Same-origin Railway is simpler and safer for the live demo.

Never commit or expose the Gemini API key in frontend code. Rotate any key posted in chat, logs, screenshots, or a public repository.

All data is synthetic. This is not an official government service and does not submit to a live department.
