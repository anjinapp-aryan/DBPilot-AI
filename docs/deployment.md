# Deployment

DBPilot AI is designed to run entirely on free-tier hosting for development
and small-scale production use.

| Component | Platform | Config |
|---|---|---|
| Frontend | [Vercel](https://vercel.com) | [deployment/vercel.json](../deployment/vercel.json) |
| Backend | [Railway](https://railway.app) or [Render](https://render.com) | [deployment/railway.json](../deployment/railway.json), [deployment/render.yaml](../deployment/render.yaml) |
| Database | [Neon PostgreSQL](https://neon.tech) | connection string via `DATABASE_URL` |

## Frontend — Vercel

1. Import the GitHub repository into Vercel.
2. Set the project root to `frontend/`.
3. Set environment variables (`NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_APP_NAME`).
4. Vercel auto-deploys on push to `main` (production) and opens preview
   deployments for pull requests.

## Backend — Railway

1. Create a new Railway project from the GitHub repo, root directory `backend/`.
2. Railway builds using the provided [backend/Dockerfile](../backend/Dockerfile).
3. Set environment variables from `.env.example` (`DATABASE_URL`, at least
   one AI provider key — e.g. `DEEP_SHEEK_NVIDIA_API_KEY` or `GEMINI_API_KEY`
   — `ALLOWED_ORIGINS`, `SECRET_KEY`).
4. Expose port `8000`; Railway provides the public URL.

## Backend — Render (alternative)

1. Create a new **Web Service** from the repo, root directory `backend/`.
2. Render reads [deployment/render.yaml](../deployment/render.yaml) for build
   (`pip install -r requirements.txt`) and start
   (`uvicorn app.main:app --host 0.0.0.0 --port $PORT`) commands.
3. Configure the same environment variables as above.

## Database — Neon

1. Create a free [Neon](https://neon.tech) project.
2. Copy the pooled connection string into `DATABASE_URL`.
3. Run Alembic migrations (introduced in Phase 2) against the Neon database
   as part of the deploy step (see `deploy.yml` workflow).

## Local (Docker Compose)

```bash
docker compose -f deployment/docker-compose.yml up --build
```

Brings up the backend, frontend, and a local Postgres instance for
development without needing cloud accounts.

## Environments

| Branch | Deploys to |
|---|---|
| `feature/*`, `bugfix/*` | Preview deployments only (PR-triggered) |
| `develop` | Staging (optional, manual trigger) |
| `main` | Production |

## CI/CD

See [.github/workflows/](../.github/workflows/) — `build.yml`,
`backend-tests.yml`, `frontend-tests.yml`, and `lint.yml` gate every PR;
`deploy.yml` handles deployment validation on `main`.
