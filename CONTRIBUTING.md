# Contributing to MAGIC Agent Skills

Thank you for your interest in contributing. This document covers everything you need to get started.

## Contributor License Agreement (CLA)

All contributors must sign the Votee Contributor License Agreement before
their pull request can be merged. The CLA will be presented automatically
when you open your first pull request via our CLA bot.

The CLA ensures that contributions are properly licensed under Apache 2.0
while protecting both contributors and the project.

*CLA document and bot integration are being finalized. Early contributors
should note that submitting a PR constitutes intent to sign the CLA once
available.*

## Code of Conduct

All contributors are expected to follow our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before participating.

## Prerequisites

- **Python 3.12+** — skills and scripts are authored against 3.12
- **Node.js 20+** — required for the CLI installer (`cli/`)
- **git**

## Development Setup

```bash
git clone https://github.com/Votee-AI/magic-agent-skills.git
cd magic-agent-skills
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Running Tests

```bash
# All tests (co-located per-skill + cross-cutting)
MPLBACKEND=Agg pytest tests/ skills/ -q --tb=short

# Cross-cutting tests only (structure, triggers, routing)
MPLBACKEND=Agg pytest tests/unit/ -q --tb=short

# Per-skill tests only (e.g., magic-data-cleaning)
MPLBACKEND=Agg pytest skills/magic-data-cleaning/tests/ -q --tb=short

# Integration tests
MPLBACKEND=Agg pytest tests/integration/ -q --tb=short

# E2E evals dry-run (validates routing logic, no LLM calls)
python tests/e2e/evals/run_evals.py --all --dry-run
```

All suites must pass before a PR is merged.

## Branch Model

| Branch | Purpose |
|--------|---------|
| `main` | Stable, released code |
| `feat/<slug>` | New features |
| `fix/<slug>` | Bug fixes |

Branch off `main`, open a PR back to `main`.

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(magic-data-synthesis): add token-cost estimator
fix(content_validator): handle empty string sentinel
docs(CONTRIBUTING): add skill contribution guide
test(routing-evals): add 4 synthesis routing cases
```

Common types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`.

## Pull Request Checklist

Before requesting review, confirm:

- [ ] All three test suites pass locally
- [ ] `CHANGELOG.md` updated under `[Unreleased]` if the change is user-facing
- [ ] New or modified skills include updated `SKILL.md` (see below)
- [ ] No hardcoded credentials or local paths
- [ ] `MPLBACKEND=Agg` set for any test that imports matplotlib

## Skill Contribution Guide

### Adding a New Skill

A skill lives under `skills/<name>/` (data skills use `magic-*`, linguistic skills use `linguistic-*`):

```
skills/<name>/
  SKILL.md            # Required — agent knowledge document
  README.md           # Required — human-readable overview
  scripts/            # Optional — reference scripts and callable tools
  references/         # Optional — additional reference material
  evals/              # Optional — routing eval cases
  tests/              # Optional — per-skill unit tests
```

### SKILL.md Frontmatter

Every `SKILL.md` must open with agentskills.io-compliant YAML frontmatter:

```yaml
---
name: magic-<name>
description: "What the skill does and when to use it. Include trigger keywords."
license: Apache-2.0
compatibility: "Python 3.12+"
metadata:
  version: "0.1.0"
  author: "Votee MAGIC Team"
  domain: data-science
  complexity: medium
  requires_llm: false
  tags:
    - data-science
    - your-tags
  scripts:
    - scripts/your_script.py
  dependencies:
    - pandas
---
```

Root-level fields (`name`, `description`, `license`, `compatibility`) follow the agentskills.io spec. All extensions go under `metadata`.

### Script Tier Markers

Every script in `scripts/` must declare its tier with a comment near the top:

```python
# SCRIPTABLE TOOL — call this script directly via CLI for heavy deterministic operations
```

or

```python
# REFERENCE IMPLEMENTATION — study and adapt; do not call directly
```

**SCRIPTABLE TOOL** scripts are safe to invoke via subprocess from agent code. They accept well-defined CLI arguments and emit structured output (JSON or TSV).

**REFERENCE IMPLEMENTATION** scripts are teaching material — the agent reads them, then writes adapted code tailored to the specific task. They may have hard-coded paths or assumptions that make direct invocation fragile.

### Evals

Add routing eval cases to `evals/evals.json`:

```json
[
  {
    "id": "my-skill-001",
    "input": "User prompt that should trigger this skill",
    "expected_skill": "magic-<name>",
    "category": "routing"
  }
]
```

Run the routing evals to validate:

```bash
python tests/e2e/evals/run_evals.py --skill magic-<name> --dry-run
```

### Modifying an Existing Skill

- Update `metadata.version` in SKILL.md frontmatter (patch for fixes, minor for new capabilities)
- Add regression eval cases covering the changed behavior
- Run the skill's co-located tests if they exist: `pytest skills/<name>/tests/`
- Validate frontmatter: `python scripts/migrate-frontmatter.py --verify`
