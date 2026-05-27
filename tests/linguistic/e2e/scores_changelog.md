# scores.json changelog

Append-only chronological log of every modification to per-skill `target_score` or `per_dim_floors_met` fields in `tests/e2e/scores.json`. Required by 0013-skill-judge-regression-ci's idempotency guard: any commit that modifies `target_score` MUST add a same-date entry here.

Format per entry:

```
## YYYY-MM-DD — <skill> <field> <old>→<new> — <one-line rationale>
```

---

## 2026-04-23 — schema baseline: target_score field already present per-skill

Initial state at the time 0013-skill-judge-regression-ci shipped: every skill in `scores.json` already has a `target_score` field at the iter-N-live block root. Floors:
- A-tier (14 skills + 1 orchestrator): `target_score: 102`
- B+ Mindset stubs (codeswitch, historical, lexicon): `target_score: 96`
- linguistic-tokenize / linguistic-scripts: `target_score: 96` (B+ original target; live overshoots to 104)
- linguistic-speech: `target_score: 96` (live 101)

The fields existed because they were authored during the live-eval pass (Wave 1-5, 2026-04-23). 0013 did NOT need to add the field — it added the CI gate that enforces them.

## 2026-04-23 — linguistic-orchestrator per_dim_floors_met false→true (after 0010)

After [`0010-orchestrator-routing-hardening`](../../openspec/changes/0010-orchestrator-routing-hardening/) shipped:
- routing_logic.md MANDATORY READ now injected from SKILL.md
- In-domain-no-match fallback section explicitly called out in MANDATORY READ
- evals/evals.json authored with 5 routing prompts

D5 (Progressive Disclosure) lifted from 11 to 12 (floor met). `per_dim_floors_met` flipped `false → true`. Total `102 → 103`. `delta_vs_target` `0 → 1`.

This is the orchestrator entry's first re-scoring after iter-2-live. Method tagged `live-skill-judge+simulated-knowledge-delta+0010-revision` to make the basis transparent.
