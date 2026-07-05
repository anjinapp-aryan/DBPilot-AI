# OBSERVABILITY.md

Target observability stack. Today's actual implementation (structlog + request/trace ID propagation) is the foundation this builds on — see [CLAUDE.md](CLAUDE.md).

## Metrics

Prometheus, scraped from every service. Core metrics: HTTP request rate/latency/error-rate (RED method) per route, AI Gateway per-provider call/success/failure/latency (already emitted by `app/ai/metrics.py` — needs an exporter, not a redesign), Kafka consumer lag per topic, DB connection pool utilization.

## Tracing

OpenTelemetry SDK, propagating the existing `X-Request-ID`/`X-Trace-ID` (`app/middleware/request_id.py`) as the trace context instead of (or alongside) a bespoke header once OTel is introduced — don't run two parallel correlation-ID systems.

## Logging

structlog JSON output (already in place, `app/core/logging.py`) shipped to a log aggregator (e.g. CloudWatch Logs or an ELK stack) with `request_id`/`trace_id`/`tenant_id` as indexed fields for fast filtering per-tenant-per-request.

## Agent Monitoring

Every `AgentStep` (see [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)) emits a structured log event with: agent name, tier, tokens used, cost, latency, tool calls made, outcome. Aggregated into an "agent health" dashboard: per-agent success rate, per-agent cost trend, validator-rejection rate for action-tier agents (a rising rejection rate is a leading indicator of a prompt regression).

## Workflow Monitoring

Per-`WorkflowRun`: full step trace queryable by `workflow_id`, so "why did the agent do that" is answerable from stored data, never requires reproducing the bug live (matches [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)'s Agent Observability). Budget-exceeded events are tracked separately from failures — a workflow correctly stopped by its budget is not the same signal as a workflow that errored.

## SLOs

| Service | SLI | SLO |
|---|---|---|
| API Gateway | p95 latency | < 500ms for non-agent routes |
| AI Gateway | end-to-end success rate (across failover chain) | ≥ 99.5% |
| Schema Discovery | completion rate | ≥ 99% (excluding genuinely unreachable connections) |
| Execution Service | validated-SQL execution success rate | ≥ 99.9% |

## SLAs

Enterprise tier only, contractual subset of the SLOs above with defined remediation/credit terms — Free/Team tiers get the SLOs as a target, not a contractual guarantee.

## Alerting

Alert on: Kafka DLQ depth growth (see [EVENTS.md](EVENTS.md)), AI Gateway "all providers down" (every provider's circuit breaker open simultaneously — currently observable via `app/ai/health.py`, needs an alert rule on top), budget-exceeded rate spike (possible cost-runaway or abuse), and any SLO burn-rate exceeding its error budget over a rolling window (standard SRE burn-rate alerting, not naive threshold-crossing).
