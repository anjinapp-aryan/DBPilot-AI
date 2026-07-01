# Contributing Guide (Detailed)

This document covers coding standards and conventions. For the quick-start
workflow (branching, commits, PR checklist), see
[CONTRIBUTING.md](../CONTRIBUTING.md) at the repo root.

## Coding Standards

### Frontend (`frontend/`)

- TypeScript strict mode; no `any` without justification.
- ESLint + Prettier enforced in CI (`lint.yml`).
- Components: functional, colocated styles, App Router conventions.

### Backend (`backend/`)

- Python 3.11+, type hints required on public functions.
- Formatting: `black`; linting: `ruff`; both enforced in CI.
- Tests: `pytest`, colocated under `backend/tests/`.
- Prefer `async def` for I/O-bound endpoints (DB, HTTP calls to DeepSeek).

## Adding a New Agent

1. Define the contract (input/output types) in
   [docs/agents.md](agents.md).
2. Add prompt templates under [prompts/](../prompts/) if the agent calls an LLM.
3. Implement under `backend/app/agents/<agent_name>/`.
4. Add unit tests under `backend/tests/agents/`.
5. Wire into the orchestrator once Phase 9 lands (before that, agents may be
   invoked directly from API routes).

## Documentation Expectations

Every feature branch should update the relevant file(s) under `docs/`
alongside the code change — treat docs drift as a bug.

## Review Process

- All changes land via PR into `develop` (or `main` for hotfixes).
- CI (`build`, `backend-tests`, `frontend-tests`, `lint`) must pass.
- At least one maintainer approval required before merge.
