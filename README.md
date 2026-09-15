# PMO Python POC

Local-only proof of concept validating the architecture proposed in
`decision-engine-poc/docs/PYTHON_STACK_PROPOSAL.md`: FastAPI + SQLAlchemy
(async) + Celery + Redis + MySQL, with a React frontend consuming an SSE
progress stream. Not deployed anywhere — this is purely to confirm the pieces
wire together and the async job pattern works before starting the real build.

## What it proves

1. React (Vite) can call a FastAPI endpoint and get a validated Pydantic
   response.
2. FastAPI can write to MySQL via async SQLAlchemy, then hand off work to a
   Celery task.
3. The Celery task (a separate process) opens its own async DB session,
   updates job status/progress, and publishes progress over Redis pub/sub.
4. FastAPI streams those pub/sub messages back to the browser as SSE, and the
   React UI renders live progress without polling.

This mirrors the exact pattern in the architecture doc's "Core Data Flow:
Spreadsheet Upload → AI Analysis" diagram, just with a trivial fake analysis
step instead of a real OpenAI call.

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (or use `pip install -e .` instead of
  the `uv` commands below)
- Node 20+
- Docker (for MySQL + Redis)

## Setup

```bash
# 1. Start MySQL + Redis
docker compose up -d

# 2. Install Python deps
uv sync

# 3. Run the migration to create the `jobs` table
uv run alembic upgrade head

# 4. Install frontend deps
cd client && npm install && cd ..
```

## Running (3 terminals)

```bash
# Terminal 1 — FastAPI
uv run uvicorn app.main:app --reload --port 8000

# Terminal 2 — Celery worker
uv run celery -A worker.celery_app worker -Q analyze --concurrency=2 --loglevel=info

# Terminal 3 — React frontend
cd client && npm run dev
```

Open http://localhost:5173, submit some text, and watch the progress bar
update live as the Celery task runs through its (simulated) steps.

## Verifying each layer independently

- **API only:** `curl -X POST localhost:8000/api/jobs -H 'Content-Type: application/json' -d '{"input_text": "hello"}'`
  — should return a job with `status: pending`.
- **DB write:** `docker compose exec mysql mysql -upmo -ppmopass pmo_poc -e 'select * from jobs;'`
- **Worker picking up the task:** watch Terminal 2's logs after the curl above
  — should show `analyze_job` received and its 4 steps.
- **SSE stream:** `curl -N localhost:8000/api/jobs/<job_id>/stream` — should
  print `data: {...}` lines as the worker progresses, ending at `status: done`.
- **Health endpoints** (same paths used in the real deployment, see
  `PYTHON_DEPLOYMENT_REQUIREMENTS.md`): `curl localhost:8000/healthz` and
  `curl localhost:8000/service/status` (the latter does a real `SELECT 1`
  against MySQL).

## What's intentionally left out (this is a wiring test, not a feature build)

- No auth (Aloha JWT) — not needed to prove the architecture
- No real OpenAI call — the "analysis" step is a word count
- No frontend framework beyond bare React (no shadcn/ui, no Tailwind, no
  Wouter) — this isn't testing UI, just the data flow
- No tests, no Docker build for the app itself, no deployment config — see
  the real deployment doc for that once this is validated
