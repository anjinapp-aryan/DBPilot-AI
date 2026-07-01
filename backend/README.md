# DBPilot AI — Backend

FastAPI application powering DBPilot AI's schema discovery, text-to-SQL,
validation, execution, explanation, and orchestration agents.

## Quick Start

```bash
python -m venv .venv
. .venv/Scripts/activate        # Windows (PowerShell: .venv\Scripts\Activate.ps1)
pip install -r requirements-dev.txt
cp ../.env.example .env
uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Testing & Quality

```bash
pytest --cov=app
ruff check .
black --check .
mypy app
```

## Structure

```text
backend/
├── app/
│   ├── main.py       # FastAPI app entrypoint
│   ├── core/          # config, settings
│   ├── api/            # HTTP route handlers
│   └── agents/          # agent implementations (Phase 2+)
└── tests/               # pytest test suite
```

See [../docs/architecture.md](../docs/architecture.md) and
[../docs/agents.md](../docs/agents.md) for design details.
