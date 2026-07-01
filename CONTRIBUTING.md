# Contributing to DBPilot AI

Thanks for your interest in contributing! This file covers the quick-start
workflow. For coding standards and architectural conventions, see
[docs/contributing.md](docs/contributing.md).

## Branching Model

- `main` — always deployable
- `develop` — integration branch for the next release
- `feature/*` — new functionality (e.g. `feature/schema-discovery`)
- `bugfix/*` — non-urgent bug fixes
- `hotfix/*` — urgent fixes branched from `main`

Branch from `develop` (or `main` for hotfixes), and open your PR back against
the branch you started from.

## Commit Convention

Commits follow [Conventional Commits](https://www.conventionalcommits.org/):

```text
feat:     new feature
fix:      bug fix
refactor: code change that neither fixes a bug nor adds a feature
docs:     documentation only
test:     adding or correcting tests
ci:       CI/CD configuration
build:    build system or dependencies
chore:    maintenance tasks
```

Example: `feat: add PostgreSQL schema discovery engine`

## Pull Request Checklist

Before opening a PR, please:

1. Run tests (`npm test` in `frontend/`, `pytest` in `backend/`).
2. Run linting (`npm run lint`, `ruff check .`).
3. Run formatting (`npm run format`, `black .`).
4. Update relevant documentation under `docs/`.
5. Fill out the PR template.

## Reporting Issues

Use the issue templates under `.github/ISSUE_TEMPLATE/` to file bugs or
feature requests.

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
