# ROADMAP.md

Long-term enterprise roadmap. `docs/roadmap.md`'s 10-phase plan is the near-term execution detail for the phases below marked ✅/🚧 — this file is the wider sequencing context, not a replacement.

## MVP (maps to `docs/roadmap.md` Phases 1-6)

Single-tenant-**shaped** (tenant_id everywhere, but no billing/quota enforcement yet), PostgreSQL-only, no Kafka (all synchronous), 3 agents: Schema Discovery, SQL Generation, SQL Validator (deterministic service, not an LLM agent). Goal: prove the core loop (connect → discover → ask → validated SQL → execute → explain) end-to-end, safely, before adding breadth.

- Phase 1 — Project bootstrap ✅ (this repo's current state)
- Phase 2 — Schema Discovery (Metadata Service's first slice, Alembic/SQLAlchemy models land here)
- Phase 3 — Text-to-SQL (SQL Generation Agent, RAG-lite: simple retrieval, no knowledge graph yet)
- Phase 4 — SQL Validation (the deterministic gate — this is the platform's most safety-critical component; do not defer)
- Phase 5 — SQL Execution
- Phase 6 — SQL Explanation

## Phase 1 (Enterprise foundations, post-MVP)

Multi-tenancy enforcement (RLS + quotas, [MULTITENANCY.md](MULTITENANCY.md)), auth (OAuth2/OIDC + RBAC, [SECURITY_ARCHITECTURE.md](SECURITY_ARCHITECTURE.md)), Knowledge Graph Agent + full hybrid RAG, Data Quality Agent, Documentation Agent.

## Phase 2 (Agent breadth)

Query Analysis, Observability, Troubleshooting, Security, Workflow Agents ([AGENTS.md](AGENTS.md)); Agent Orchestrator with plan-then-execute budgeting ([AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)); Kafka introduced for schema-discovery/indexing async paths ([EVENTS.md](EVENTS.md)) — the first point where event-driven architecture actually earns its cost.

## Phase 3 (Second database engine + Migration Agent)

Prove the Connection/driver abstraction generalizes by adding one more engine (MySQL, most similar dialect to Postgres of the remaining list — lowest integration risk to validate the abstraction). Migration Agent ships once there's a real second-engine migration use case to design against, not speculatively.

## Enterprise Phase

Compliance certification work (SOC 2, [SECURITY_ARCHITECTURE.md](SECURITY_ARCHITECTURE.md)), SLA tier for Enterprise customers ([OBSERVABILITY.md](OBSERVABILITY.md)), remaining database engines (Oracle, SQL Server, MongoDB, Cassandra, Snowflake, BigQuery, Redshift, Databricks) prioritized by actual customer demand, not the full list at once.

## Scale Phase

Kubernetes/EKS migration (triggered by genuine multi-service operational need, not calendar time — see [DECISIONS.md](DECISIONS.md) ADR-022), control-plane/data-plane independent scaling fully realized ([ARCHITECTURE.md](ARCHITECTURE.md)), read replicas + sharding for the app database ([DATABASE.md](DATABASE.md)) once a single Postgres primary is the actual bottleneck (measured, not assumed).

## Sequencing Principle

Each phase above earns the next — Kafka isn't adopted until MVP proves the synchronous path is genuinely too slow for a real workflow; Kubernetes isn't adopted until Docker Compose/Railway genuinely can't scale the current service count. This roadmap deliberately avoids front-loading infrastructure the platform hasn't yet demonstrated it needs (the cost-concern risk flagged in this doc set's initial analysis).
