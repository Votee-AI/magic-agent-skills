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
# Unit tests (fast, no external dependencies)
MPLBACKEND=Agg pytest tests/unit/ -q --tb=short

# Integration tests (may require network/filesystem fixtures)
MPLBACKEND=Agg pytest tests/integration/ -q --tb=short

# E2E evals dry-run (validates routing logic, no LLM calls)
python tests/e2e/evals/run_evals.py --all --dry-run
```

All three suites must pass before a PR is merged.

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

A skill lives under `skills/magic-<name>/` and must contain:

```
skills/magic-<name>/
  SKILL.md            # Required — skill specification
  scripts/            # Reference scripts and callable tools
  evals/
    evals.json        # Required — routing eval cases
```

### SKILL.md Frontmatter

Every `SKILL.md` must open with YAML frontmatter:

```yaml
---
name: magic-<name>
version: 1.0.0
description: One-sentence description of what the skill does.
triggers:
  - keyword one
  - keyword two
---
```

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

- Update `SKILL.md` version in frontmatter (patch for fixes, minor for new capabilities)
- Add regression eval cases covering the changed behavior
- Update `CHANGELOG.md`
