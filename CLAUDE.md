# CLAUDE.md

Guidance for AI coding agents (Claude Code, Cursor, etc.) working in this repository.

## What this repo is

MAGIC Agent Skills is a collection of **30 agent skills** for LLM training-data
preparation, data science, and computational linguistics. Each skill is a
self-contained directory under `skills/` with a `SKILL.md` (frontmatter +
instructions), optional `scripts/`, and co-located `tests/`.

The `cli/` directory is a **thin TypeScript installer** (`@votee-ai/magic-agent-skills`)
that fetches skills from GitHub at runtime — it does **not** bundle skill content.

## Repository layout

| Path | Purpose |
|------|---------|
| `skills/magic-data-*` | Data-agent skills (loading, cleaning, synthesis, …) |
| `skills/magic-linguistic-*` | Computational-linguistics skills |
| `skills/_linguistic_shared/` | Shared resources for linguistic skills |
| `cli/` | Thin Node CLI installer (runtime GitHub fetch) |
| `schema/SKILL.schema.json` | JSON Schema all `SKILL.md` frontmatter must satisfy |
| `.claude-plugin/marketplace.json` | Claude plugin marketplace grouping |
| `skills.sh.json` | skills.sh leaderboard grouping |
| `tests/` | Cross-cutting tests (`shared/`, `data-agent/`, `linguistic/`) |
| `.github/workflows/` | CI (tests, schema validation, package content, license, release) |

## Working conventions

- **Adding/editing a skill:** every `SKILL.md` frontmatter must validate against
  `schema/SKILL.schema.json`. Run the schema-validation step before committing.
- **Tests:** `pytest tests/shared/ tests/data-agent/ tests/linguistic/`. Use
  `MPLBACKEND=Agg` for anything touching matplotlib.
- **CLI:** `cd cli && npm ci && npm run build && npm test`. Keep it thin — CI
  fails if `skills/` or `commands/` get bundled into the package.
- **Match the surrounding style** of whatever file you touch; skills follow a
  consistent SKILL.md structure — mirror a neighboring skill when creating one.

## Before you finish

Run the relevant tests and the schema validation. CI enforces: unit tests, CLI
tests, schema validation, methodology validation, package content (thin CLI),
and license checks (no GPL/AGPL/SSPL).

See `CONTRIBUTING.md` for setup, branch model, and PR expectations.
