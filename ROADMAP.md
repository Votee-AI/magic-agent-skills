# Roadmap

MAGIC Agent Skills is a collection of agent skills for LLM training-data preparation,
data science, and computational linguistics. This roadmap shows where the project is
heading. Plans evolve — for the live picture and to weigh in, see the
[issue tracker](https://github.com/Votee-AI/magic-agent-skills/issues).

Each item links back to a tracked milestone. Dates are intentionally omitted in favor
of phase ordering (Now / Next / Later).

## Phase A — Now: Unified open-source launch

Ship the unified repository publicly with all skills, a thin installer, and green CI.

- ✅ 30 skills unified under `skills/` (data-agent + computational-linguistics)
- ✅ `SKILL.md` schema + frontmatter validation in CI
- ✅ Thin CLI installer (`@votee-ai/magic-agent-skills`) — fetches skills at install time
- ✅ Distribution manifests: Claude plugin marketplace + skills.sh leaderboard
- 🚧 Pre-public governance: license inventory, env-var reference, roadmap, contributor guide
- 🚧 Community/repo hygiene: labels, PR/issue templates, dependency automation
- ⏳ First public release + npm publish

## Phase B — Next: Methodology framework & evaluation

Grow the synthesis skill from a generation **engine** into a library of documented,
reproducible **data-crafting methodologies** (per training stage), each with a
runnable, engine-validated template and an evaluation harness.

- Stage-organized methodologies: pre-training, SFT, RL, reasoning, evaluation
- Runnable templates validated against the synthesis engine
- An evaluation/quality harness so each methodology ships trainer-ready by default

## Phase C — Later: Optimization & expansion

Broaden coverage and optimize the ecosystem based on real usage.

- New data skills (additional formats, sources, and extraction capabilities)
- Performance and cost optimization across the pipeline
- Deeper tooling for composing skills into end-to-end pipelines
- Documentation site as the canonical home for guides and tutorials

---

## How to influence the roadmap

- **Open an issue** for bugs, ideas, or skill requests.
- **Start a discussion** for larger directional proposals.
- **Contribute** — see [`CONTRIBUTING.md`](CONTRIBUTING.md).

Priorities are driven by community needs and maintainer capacity; nothing here is a
commitment to a specific date or order.
