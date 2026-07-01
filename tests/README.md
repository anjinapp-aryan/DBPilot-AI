# Cross-Cutting Tests

Unit tests live alongside the code they test (`backend/tests/` for the
FastAPI app, `frontend/app/__tests__/` for the Next.js app). This directory
is reserved for **end-to-end and integration tests that span both services**
(e.g. "ask a question in the UI → verify the SQL that was generated and
executed"), introduced starting Phase 9 (multi-agent orchestration) once
there's a full request path to exercise.

## Status

Empty for Phase 1 — see [../docs/roadmap.md](../docs/roadmap.md).
