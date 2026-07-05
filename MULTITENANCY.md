# MULTITENANCY.md

## Tenant Isolation

**Decision: row-level isolation (shared schema, `tenant_id` column + Postgres Row-Level Security) over schema-per-tenant or database-per-tenant.** Rationale: DBPilotAI's tenant count is expected to grow into the hundreds/thousands (SaaS model, not a handful of large enterprise deployments each warranting a dedicated DB) — schema-per-tenant doesn't scale operationally past low hundreds of tenants (migration fan-out, connection pool exhaustion). RLS enforces isolation at the database layer, not just application-layer WHERE clauses, so a missed `tenant_id` filter in application code fails closed instead of leaking data (see the risk noted in the analysis this doc set is built from).

```sql
ALTER TABLE connections ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON connections
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

The application sets `app.current_tenant_id` from the authenticated request's JWT claim at the start of every request/session — never trusts a `tenant_id` passed in a request body for filtering (only for validation that it matches the session's tenant).

## Database Strategy

Single shared Postgres cluster for control-plane data (tenants, connections, metadata) — sharded by tenant_id hash once a single cluster's write throughput becomes the bottleneck (not needed at MVP scale). Vector store similarly shared with tenant-scoped filtering at the query layer ([RAG_ARCHITECTURE.md](RAG_ARCHITECTURE.md)).

## Security Boundaries

RLS is defense-in-depth, not the only layer: the API Gateway's authorization middleware checks tenant scope before a request reaches a service; the service layer checks again before a DB query; RLS is the last line if both of those are somehow bypassed. Three layers, not one.

## Resource Management

Per-tenant resource ceilings enforced by `BudgetEnforcementService` ([DOMAIN.md](DOMAIN.md)): max concurrent agent workflows, max connections, max monthly query executions. A tenant hitting a limit gets a clear, immediate rejection — never silent throttling that looks like a platform bug.

## Quotas

| Tier | Connections | Monthly agent workflow cost | Concurrent workflows |
|---|---|---|---|
| Free | 1 | Fixed low ceiling | 1 |
| Team | 10 | Mid ceiling | 5 |
| Enterprise | Unlimited (contractual) | Contractual, monitored not hard-capped | Contractual |

## Billing Strategy

Usage-metered (agent workflow cost, query execution count) rather than flat-seat pricing, since the platform's actual cost driver is LLM token spend and compute for schema-discovery/RAG-indexing jobs, not per-seat — flat pricing would misalign cost and price at the tails (a Free-tier tenant running huge discovery jobs, or an Enterprise tenant with light usage). Metering data comes from the same `orchestration`/`execution` audit tables already required for compliance ([DATABASE.md](DATABASE.md)) — billing is a read model over data that exists anyway, not a separate tracking system.
