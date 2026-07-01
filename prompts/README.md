# Prompts

LLM prompt templates used by DBPilot AI's agents (see
[../docs/agents.md](../docs/agents.md)). Each template is versioned as a
plain text/markdown file so prompt changes are reviewable in diffs,
independent of application code changes.

## Conventions

- One file per agent/purpose, named `<agent>.md` (e.g. `text-to-sql.md`).
- Templates use `{{variable}}` placeholders, rendered by the backend before
  being sent to the LLM.
- Never embed secrets or real schema/data in committed templates — use
  placeholder examples only.

## Status

Populated starting Phase 3 (Text-to-SQL). See
[text-to-sql.md](text-to-sql.md) for the first template.
