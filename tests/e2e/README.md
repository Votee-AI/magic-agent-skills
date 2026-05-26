# E2E Tests

End-to-end tests that validate full data processing pipelines, agent workflow simulation, and skill routing.

## Running Tests

```bash
# All e2e tests
pytest tests/e2e/ -v

# Smoke test — runs all 32+ scripts against synthetic data
bash tests/e2e/reverify_all.sh

# Eval dry-run — validates routing eval JSON structure
python tests/e2e/evals/run_evals.py --all --dry-run
```

## Test Files

| File | What it tests |
|------|---------------|
| `test_e2e_scenarios.py` | Full pipeline, self-healing, text analysis scenarios |
| `test_agent_workflow_simulation.py` | Simulates agent behavior: lifecycle routing → script execution → output verification |
| `test_workflow_reinforcement.py` | Validates SKILL.md structural prerequisites for correct agent behavior |
| `test_interactive_features.py` | Workspace state, PAUSE gates, checkpoint flows |
| `test_datadesigner_integration.py` | DataDesigner template validation and preview (requires `data-designer` + API key) |

## Utilities

| File | Purpose |
|------|---------|
| `scenario_runner.py` | Programmatic scenario execution engine |
| `verify_scenario.py` | Output verification logic |
| `generate_e2e_data.py` | Generates synthetic datasets for tests |
| `reverify_all.sh` | Smoke test — runs every script CLI end-to-end |
| `run_agent_tests.py` | Agent test orchestrator (setup, score, report) |

## Directories

| Directory | Contents |
|-----------|----------|
| `datasets/` | Synthetic test data (CSV, JSONL) used by tests |
| `scenarios/` | Scenario definitions for `scenario_runner.py` |
| `expected/` | Expected outputs for scenario verification |
| `evals/` | Routing eval assertions (`evals.json`, `cross_skill_evals.json`) |
| `deep-eval/` | Scale testing with large generated datasets |

## Real Data Testing

The `realdata/` directory (gitignored) is for testing with your own datasets. Real data surfaces edge cases that synthetic data misses. See [tests/README.md](../README.md) for guidance on contributing real data tests.
