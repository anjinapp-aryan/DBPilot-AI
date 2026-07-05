# SKILLS.md

Full technology inventory for DBPilotAI. **Status column** distinguishes what's actually in the repo today from the target stack — don't assume something is available just because it's listed here.

## Languages

| Tech | Status | Notes |
|---|---|---|
| Python 3.11/3.12 | ✅ In use | Backend. CI matrix tests both. |
| TypeScript (strict) | ✅ In use | Frontend, `tsconfig.json` `strict: true`. |
| SQL (PostgreSQL dialect) | 🎯 Target | For generated queries + migrations. |

## Frameworks

| Tech | Status | Notes |
|---|---|---|
| FastAPI | ✅ In use | ASGI, async-first — replaces Spring Boot/WebFlux in the original enterprise template. |
| Pydantic v2 | ✅ In use | Settings + request/response models. |
| SQLAlchemy 2.x (async) + Alembic | 🎯 Target | `app/core/db.py` has the engine/session plumbing; no models/migrations yet (Phase 2). |
| Next.js (App Router) + React | ✅ In use | Frontend. |
| structlog | ✅ In use | Structured logging (`app/core/logging.py`). |
| tenacity | ✅ In use | Retry policy for AI provider calls. |

## Databases

| Tech | Status | Notes |
|---|---|---|
| PostgreSQL (Neon) | 🎯 Target (config only) | App DB + first supported target-database engine. |
| Redis | 🎯 Target | Cache/session store; `InMemoryCache` (`app/core/cache.py`) is the interim implementation behind the same `CacheProvider` protocol. |
| Vector DB (pgvector or Qdrant) | 🎯 Target | See [RAG_ARCHITECTURE.md](RAG_ARCHITECTURE.md) for the decision criteria. |
| Future DB engine support | 🎯 Target | Oracle, MySQL, SQL Server, MongoDB, Cassandra, Snowflake, BigQuery, Redshift, Databricks — see [ROADMAP.md](ROADMAP.md) for sequencing. |

## Cloud / Infra

| Tech | Status | Notes |
|---|---|---|
| AWS | 🎯 Target | Primary cloud. |
| Docker / Docker Compose | ✅ In use | Local dev (`deployment/docker-compose.yml`), per-service Dockerfiles. |
| Kubernetes / AWS EKS | 🎯 Target | Production orchestration — not needed until multi-service scale (see [ROADMAP.md](ROADMAP.md) "Scale phase"). |
| Terraform | 🎯 Target | IaC for AWS resources. |
| Vercel (frontend) / Railway or Render (backend, pre-K8s) | ✅ Configured | `deployment/vercel.json`, `deployment/railway.json`, `deployment/render.yaml`. |

## AI Technologies

| Tech | Status | Notes |
|---|---|---|
| Multi-provider LLM gateway (custom) | ✅ In use | `app/ai/` — DeepSeek/Gemini/Groq/Qwen/OpenRouter failover. This is DBPilotAI's own "Spring AI equivalent." |
| Multi-agent orchestration | 🎯 Target | [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md) — extends the gateway's resilience pattern. |
| MCP (Model Context Protocol) | 🎯 Target | Standardized tool-calling interface for agents. |
| Tool calling | 🎯 Target | Per-agent tool contracts, see [AGENTS.md](AGENTS.md). |
| RAG / vector search | 🎯 Target | See [RAG_ARCHITECTURE.md](RAG_ARCHITECTURE.md). |
| Knowledge graph | 🎯 Target | Schema/lineage relationships — see [RAG_ARCHITECTURE.md](RAG_ARCHITECTURE.md). |
| Agent memory | 🎯 Target | See [MEMORY.md](MEMORY.md). |

## Architecture Patterns

Hexagonal/Clean Architecture, Domain-Driven Design, Event-Driven Architecture (selective — see [EVENTS.md](EVENTS.md)), CQRS (where read/write load genuinely diverges), SOLID.

## Design Patterns (in active use today)

- **Strategy** — `LlmProvider` implementations (`app/ai/providers/`).
- **Circuit Breaker** — `app/ai/circuit_breaker.py`.
- **Dependency Injection** — `app/core/dependencies.py`.
- **Protocol/interface segregation** — `CacheProvider` (`app/core/cache.py`).

## DevOps Stack

GitHub Actions (build, backend-tests, frontend-tests, lint+security-scan, deploy-validation), Gitleaks (secret scanning, full-history), Dependabot, ruff/black/mypy, ESLint/Prettier, pytest/vitest.

## Observability Stack

| Tech | Status |
|---|---|
| structlog (JSON in non-dev envs) | ✅ In use |
| Request/trace ID propagation | ✅ In use (`app/middleware/request_id.py`) |
| OpenTelemetry | 🎯 Target — see [OBSERVABILITY.md](OBSERVABILITY.md) |
| Prometheus / Grafana | 🎯 Target |

## Security Stack

| Tech | Status |
|---|---|
| Gitleaks (secret scanning) | ✅ In use |
| CORS (`allowed_origins`) | ✅ In use, permissive default — tighten before auth ships |
| JWT / OAuth2 | 🎯 Target — see [SECURITY.md](SECURITY.md) |
| RBAC | 🎯 Target |
| Per-tenant envelope encryption for stored credentials | 🎯 Target (critical path — see [SECURITY.md](SECURITY.md) and [MULTITENANCY.md](MULTITENANCY.md)) |
