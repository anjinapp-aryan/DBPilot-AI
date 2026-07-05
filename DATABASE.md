# DATABASE.md

Target design for DBPilotAI's **own** application database (PostgreSQL/Neon). Not to be confused with the customer target-databases DBPilotAI connects to — see [DOMAIN.md](DOMAIN.md)'s Connection/Execution contexts for that distinction, and `docs/database.md` for the current, much smaller Phase-1-scoped version of this file.

## Database Design

One PostgreSQL database, schema-per-concern (not schema-per-tenant — see [MULTITENANCY.md](MULTITENANCY.md) for why row-level `tenant_id` + RLS is preferred over schema-per-tenant at this stage):

- `tenancy` — tenants, quotas, users, roles.
- `connections` — encrypted connection records.
- `metadata` — schemas, tables, columns, glossary, lineage (mirrors [DOMAIN.md](DOMAIN.md) aggregates).
- `execution` — query execution records, audit log.
- `orchestration` — workflow runs, agent steps.

## Metadata Schema (core tables, illustrative)

```sql
-- tenancy
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    tier TEXT NOT NULL DEFAULT 'free',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- connections
CREATE TABLE connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    engine_type TEXT NOT NULL,
    encrypted_credential BYTEA NOT NULL,      -- envelope-encrypted, see SECURITY.md
    encryption_key_id TEXT NOT NULL,          -- which tenant DEK encrypted this row
    status TEXT NOT NULL DEFAULT 'pending',
    last_health_check_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_connections_tenant ON connections(tenant_id);

-- metadata
CREATE TABLE schemas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connection_id UUID NOT NULL REFERENCES connections(id),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    version INT NOT NULL DEFAULT 1,
    discovered_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_schemas_tenant ON schemas(tenant_id);

CREATE TABLE tables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schema_id UUID NOT NULL REFERENCES schemas(id),
    tenant_id UUID NOT NULL,                  -- denormalized for RLS, see MULTITENANCY.md
    name TEXT NOT NULL,
    row_count_estimate BIGINT,
    UNIQUE (schema_id, name)
);

-- execution
CREATE TABLE query_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    connection_id UUID NOT NULL REFERENCES connections(id),
    validated_sql TEXT NOT NULL,
    status TEXT NOT NULL,
    row_count INT,
    duration_ms INT,
    requested_by UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
) PARTITION BY RANGE (created_at);         -- see Partitioning below
```

## Naming Conventions

- Tables: plural snake_case (`connections`, `query_executions`).
- Primary keys: `id` (UUID, `gen_random_uuid()` default) — never auto-increment integers, to avoid cross-tenant enumeration.
- Foreign keys: `<referenced_table_singular>_id`.
- Timestamps: `created_at`/`updated_at`, always `TIMESTAMPTZ`, always UTC.
- Every tenant-scoped table has `tenant_id` as a real (denormalized where needed) column — never inferred through a join, so Row-Level Security policies can reference it directly (see [MULTITENANCY.md](MULTITENANCY.md)).

## Partitioning

`query_executions` and `execution_audit_log` (high-write, time-series, compliance-retention-driven) are range-partitioned by `created_at`, monthly. Old partitions are moved to cheaper storage or dropped per the tenant's audit-retention policy, not deleted row-by-row.

## Indexing

- Every foreign key gets a btree index (Postgres doesn't auto-create these).
- Every tenant-scoped table's `tenant_id` is indexed (and is the leading column in any composite index used for tenant-scoped list queries).
- `pgvector` (if used for the vector store, see [RAG_ARCHITECTURE.md](RAG_ARCHITECTURE.md)) uses an HNSW or IVFFlat index per the embedding table, sized by expected corpus size, not left at default.

## Audit Strategy

`execution_audit_log` is append-only (no `UPDATE`/`DELETE` grants at the DB role level — enforced by Postgres `GRANT`, not just application logic) and records every attempted execution, approved or rejected, with the validator's reasoning for rejections. This is the system of record for compliance review (see [SECURITY.md](SECURITY.md)).

## Versioning

Alembic migrations, one linear history (no branching migration heads in `main`). `schemas.version` increments on structural re-discovery so Metadata/RAG consumers can detect "this cached embedding is against a stale schema version" without re-diffing the whole schema.

## Backup Strategy

- Continuous WAL archiving + daily full snapshot (managed Postgres, e.g. Neon's point-in-time recovery).
- `encryption_key_id`-referenced key material backed up **separately** from the database snapshot (see [SECURITY.md](SECURITY.md) — losing the key without losing the DB, or vice versa, must both be recoverable independently).

## Performance Strategy

- Read replicas for Metadata/RAG-heavy read paths once a single primary can't keep up; `query_executions`/audit writes stay on the primary (write-heavy, partitioned).
- Connection pooling (PgBouncer or equivalent) between the FastAPI app and Postgres — SQLAlchemy's own pool is per-process, not shared across horizontally-scaled API instances.
- Aggressive caching (Redis, see [MEMORY.md](MEMORY.md)) in front of Metadata reads — schema/glossary/lineage change far less often than they're read.
