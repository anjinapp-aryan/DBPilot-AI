# Roadmap

DBPilot AI is built incrementally, one phase per feature branch, each ending
in a tested, documented, merged milestone.

| Phase | Milestone | Branch | Status |
|---|---|---|---|
| 1 | Project bootstrap | `feature/project-bootstrap` | 🚧 In progress |
| 2 | Schema discovery | `feature/schema-discovery` | ⬜ Planned |
| 3 | Text-to-SQL | `feature/text-to-sql` | ⬜ Planned |
| 4 | SQL validation | `feature/sql-validator` | ⬜ Planned |
| 5 | SQL execution | `feature/sql-executor` | ⬜ Planned |
| 6 | SQL explanation | `feature/sql-explainer` | ⬜ Planned |
| 7 | Voice support | `feature/voice-agent` | ⬜ Planned |
| 8 | Visualization | `feature/chart-agent` | ⬜ Planned |
| 9 | Multi-agent orchestration | `feature/multi-agent` | ⬜ Planned |
| 10 | Production deployment | `feature/deployment` | ⬜ Planned |

## Phase Details

### Phase 1 — Project Bootstrap
Monorepo structure, CI/CD skeleton, documentation set, minimal working
frontend/backend scaffolds with a health check.

### Phase 2 — Schema Discovery
Introspect a connected PostgreSQL database (tables, columns, keys, indexes)
and expose it via the API; cache results for use as LLM grounding context.

### Phase 3 — Text-to-SQL
DeepSeek-backed agent that turns a natural-language question + schema
context + conversation history into a candidate SQL statement.

### Phase 4 — SQL Validation
Deterministic safety gate that blocks destructive/unauthorized SQL before
execution.

### Phase 5 — SQL Execution
Sandboxed execution with row limits, timeouts, and audit logging.

### Phase 6 — SQL Explanation
Plain-English explanations of generated SQL; optional "tutor mode."

### Phase 7 — Voice Support
Browser-based speech-to-text for hands-free querying.

### Phase 8 — Visualization
Automatic chart-type selection and rendering based on result shape.

### Phase 9 — Multi-Agent Orchestration
Formal orchestrator coordinating all agents with streaming progress updates.

### Phase 10 — Production Deployment
Hardened deploy to Vercel (frontend), Railway/Render (backend), and Neon
(database), with full CI/CD gating.

## Tracking

Each phase maps to a GitHub milestone with the same name — see the
[Milestones](https://github.com/anjinapp-aryan/DBPilot-AI/milestones) page.
