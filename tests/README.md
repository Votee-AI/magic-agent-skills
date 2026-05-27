# Testing Guide

## Test Tiers

| Tier | Command | What it validates |
|------|---------|-------------------|
| **Unit** | `MPLBACKEND=Agg pytest tests/unit/ skills/*/tests/ -q` | Individual script correctness — co-located in `skills/*/tests/` + cross-cutting in `tests/unit/` |
| **Integration** | `MPLBACKEND=Agg pytest tests/integration/ -q` | Multi-script workflows, NL routing, checkpoint flows |
| **E2E** | `pytest tests/e2e/ -q` | Full pipeline scenarios, agent workflow simulation |
| **Eval** | `python tests/e2e/evals/run_evals.py --all --dry-run` | Skill routing eval assertions (JSON structure validation) |
| **Smoke** | `bash tests/e2e/reverify_all.sh` | Runs all 32+ scripts against synthetic data end-to-end |

Run all automated tests:
```bash
MPLBACKEND=Agg pytest tests/ skills/ -q --tb=short
```

## Manual Testing

Automated tests validate script correctness and structural consistency. For comprehensive validation, we recommend also running **manual agent tests** — give your AI coding assistant real data tasks and verify the full flow works end-to-end.

**Suggested manual test flow:**
1. Install skills into your agent (`npx @votee-ai/magic-agent-skills init`)
2. Give the agent a CSV/JSONL file and say: *"Load and profile this data"*
3. Follow through: cleaning, transformation, visualization, reporting
4. Verify each step produces correct output and the agent follows SKILL.md patterns

### Real Data Testing

We strongly recommend testing with **your own real datasets**. Synthetic test data covers structural correctness, but real data surfaces edge cases that synthetic data misses — encoding issues, unexpected column types, domain-specific patterns, and data quality problems.

To contribute real data tests:
1. Create a directory under `tests/e2e/realdata/<your-dataset>/`
2. Add a small sample (keep it under 1MB, no proprietary data)
3. Add a scenario description and expected outcomes
4. The directory is gitignored by default — open a PR to discuss inclusion

## Skill Quality Assessment

We use two community tools to assess and improve skill quality:

- **[Skill Creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)** — Anthropic's skill authoring tool for creating, evaluating, and optimizing SKILL.md files
- **[Skill Judge](https://github.com/softaworks/agent-toolkit/blob/main/skills/skill-judge/README.md)** — Independent skill quality evaluator with multi-dimensional scoring

These tools help ensure our skills follow best practices for agent consumption. Contributors can use them to validate new skills or improvements before submitting PRs.

## Directory Structure

```
tests/
├── README.md                  ← You are here
├── unit/                      ← Script-level tests (805+ tests)
│   ├── test_data/             ← Fixture CSV/JSONL files
│   └── test_*.py              ← Cross-cutting validation tests
├── integration/               ← Multi-script workflow tests
├── e2e/                       ← End-to-end pipeline tests
│   ├── datasets/              ← Synthetic test data
│   ├── scenarios/             ← Scenario definitions
│   ├── evals/                 ← Routing eval assertions
│   ├── deep-eval/             ← Scale testing scripts
│   └── reverify_all.sh        ← Smoke test all scripts
├── fixtures/                  ← DB fixture creator
└── generate_test_data.py      ← Synthetic data generator
```
