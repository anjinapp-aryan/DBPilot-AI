# DBPilot AI — Frontend

Next.js (App Router, TypeScript) application for DBPilot AI's chat UI,
schema explorer, and chart rendering.

## Quick Start

```bash
npm install
cp ../.env.example .env.local
npm run dev
```

App runs at http://localhost:3000.

## Testing & Quality

```bash
npm run type-check
npm run test
npm run lint
npm run format:check
```

## Structure

```text
frontend/
├── app/            # App Router pages, layouts, tests
├── next.config.mjs
├── tsconfig.json
└── vitest.config.ts
```

See [../docs/architecture.md](../docs/architecture.md) for design details.
