# Testing Guide

## Test Tiers

| Tier | Command | What it validates |
|------|---------|-------------------|
| **Structural** | `MPLBACKEND=Agg pytest tests/shared/ -q` | SKILL.md frontmatter, triggers, script references across all 30 skills |
| **Unit (data-agent)** | `MPLBACKEND=Agg pytest tests/data-agent/unit/ -q` | Data-agent skill script correctness |
| **Unit (linguistic)** | `MPLBACKEND=Agg pytest tests/linguistic/unit/ -q` | Linguistic skill script correctness |
| **Integration** | `MPLBACKEND=Agg pytest tests/data-agent/integration/ tests/linguistic/integration/ -q` | Multi-script workflows, NL routing, checkpoint flows |
| **E2E** | `pytest tests/data-agent/e2e/ -q` | Full pipeline scenarios, agent workflow simulation |
| **Eval** | `python tests/data-agent/e2e/evals/run_evals.py --all --dry-run` | Skill routing eval assertions (JSON structure validation) |
| **CLI** | `cd cli && npm test` | CLI installer tests (42 tests) |

Run all Python tests:
```bash
MPLBACKEND=Agg pytest tests/ -q --tb=short
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

## Skill Quality Assessment

We use two community tools to assess and improve skill quality:

- **[Skill Creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)** — Anthropic's skill authoring tool for creating, evaluating, and optimizing SKILL.md files
- **[Skill Judge](https://github.com/softaworks/agent-toolkit/blob/main/skills/skill-judge/README.md)** — Independent skill quality evaluator with multi-dimensional scoring

## Directory Structure

```
tests/
├── README.md                          ← You are here
├── shared/                            ← Cross-cutting structural tests (all 30 skills)
│   ├── test_skill_structure.py
│   ├── test_nl_triggers.py
│   ├── test_script_references.py
│   └── ...
├── data-agent/
│   ├── unit/                          ← Data-agent skill script tests
│   ├── integration/                   ← Multi-skill workflow tests
│   └── e2e/
│       └── evals/                     ← Routing eval assertions
├── linguistic/
│   ├── unit/                          ← Linguistic skill script tests
│   ├── integration/                   ← Linguistic workflow tests
│   └── e2e/                           ← Linguistic e2e tests
├── test_data/                         ← Fixture CSV/JSONL files
├── fixtures/                          ← DB fixture creator
└── generate_test_data.py              ← Synthetic data generator
```
