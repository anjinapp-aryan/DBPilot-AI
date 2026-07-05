# EVENTS.md

Kafka is used **only** where genuine async decoupling, fan-out, or long-running-job semantics are needed — not by default for every internal call (see [CLAUDE.md](CLAUDE.md)'s Forbidden Patterns and the risk noted in the analysis that produced this doc set: event-driven architecture has a real operational cost).

## Criteria: does this need to be an event?

Ask before adding a topic: (1) does the producer need to *not* wait for the consumer (true async)? (2) are there multiple independent consumers? (3) can this legitimately take longer than a synchronous HTTP request should? If none are true, it's a function call or a synchronous HTTP route, not a Kafka topic.

## Kafka Topics

| Topic | Producer | Consumer(s) | Why it's an event |
|---|---|---|---|
| `schema.discovery.requested` | API Gateway | Metadata Service | Discovery can take minutes on a large schema; user shouldn't block on it |
| `schema.discovery.completed` | Metadata Service | API Gateway (notify user), Vector Store indexer | Multiple independent consumers |
| `schema.discovery.failed` | Metadata Service | API Gateway | Same as above |
| `metadata.embedding.requested` | Metadata Service | Vector indexing worker | Bulk re-embedding is a bursty background job |
| `workflow.run.started` / `.completed` / `.budget_exceeded` | Agent Orchestrator | Observability pipeline, billing/quota service | Cross-cutting consumers that shouldn't couple to the orchestrator's request path |
| `execution.audit.recorded` | Execution Service | Audit/compliance pipeline, Security Agent | Compliance consumer must never be able to slow down or block actual execution |

Explicitly **not** events: a single chat turn's request/response, a single agent's tool call, a CRUD operation on `connections` — all synchronous HTTP.

## Event Taxonomy

`<domain>.<entity>.<past-tense-verb>` — e.g. `schema.discovery.completed`, `execution.audit.recorded`. Domain matches the bounded contexts in [DOMAIN.md](DOMAIN.md).

## Event Contracts

Every event is a versioned, schema-registry-validated payload (Avro or JSON Schema — JSON Schema preferred for a Python-first stack, lower tooling overhead than Avro without sacrificing validation). Minimum envelope:

```json
{
  "event_id": "uuid",
  "event_type": "schema.discovery.completed",
  "event_version": 1,
  "tenant_id": "uuid",
  "occurred_at": "2026-01-01T00:00:00Z",
  "payload": { "...": "event-specific fields" }
}
```

## Event Ownership

The producing bounded context owns the schema — Metadata Service owns `schema.discovery.*` contracts; consumers depend on the contract, never reach into the producer's internal representation.

## Retry Policies

Consumer-side retry with exponential backoff, max 5 attempts, only for transient failures (matches the [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)/`app/ai/` philosophy of retrying only what's actually retryable) — a malformed payload or a business-logic rejection is not retried, it goes straight to the DLQ.

## DLQ Strategy

Every topic has a corresponding `<topic>.dlq`. A message lands there after retry exhaustion or on a non-retryable failure, with the failure reason attached. DLQ depth is alerted on (see [OBSERVABILITY.md](OBSERVABILITY.md)) — a growing DLQ is treated as an incident, not background noise.

## Event Versioning

Additive changes (new optional field) don't bump `event_version`. Breaking changes (field removal/type change) bump the version and the producer publishes both versions during a deprecation window until all consumers migrate — no big-bang consumer/producer coordinated deploys.
