# Agents (Specs)

This directory holds **agent specifications** — human-readable contracts for
each agent's inputs, outputs, and constraints. Implementation code lives in
`backend/app/agents/`; prompt text lives in [../prompts/](../prompts/); the
full design rationale is in [../docs/agents.md](../docs/agents.md).

## Why specs are separate from implementation

Keeping the contract (this directory) separate from the implementation
(`backend/app/agents/`) lets the spec be reviewed and agreed on before code
is written, and gives each agent a stable, versioned interface that other
agents/tests can rely on regardless of internal implementation changes.

## Roster

| Spec file | Phase | Status |
|---|---|---|
| `schema-discovery.md` | 2 | Planned |
| `text-to-sql.md` | 3 | Planned |
| `sql-validator.md` | 4 | Planned |
| `sql-executor.md` | 5 | Planned |
| `sql-explainer.md` | 6 | Planned |
| `chart.md` | 8 | Planned |
| `orchestrator.md` | 9 | Planned |

Specs are added as each phase is implemented — see
[../docs/roadmap.md](../docs/roadmap.md).
