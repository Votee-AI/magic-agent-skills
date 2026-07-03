<!-- Natural Language Triggers: "full pipeline", "lifecycle workflow", "set up pipeline", "structured data processing", "what phase are we in?", "lifecycle status" -->

# /data:lifecycle — Full Data Processing Pipeline

Run a comprehensive, phased data processing workflow with quality gates, progress tracking, and structured decision recording.

**Step 1:** Read the `magic-data-lifecycle` SKILL.md for routing knowledge — understand pipeline ordering and which skill handles each operation.

**Step 2:** Assess complexity tier and match infrastructure:

| Tier | Trigger | Infrastructure | Example |
|------|---------|---------------|---------|
| **Tier 1** | Single, specific operation | No workspace_state.md, no data-spec.md. Load → auto-profile → execute → validate → done. | "Clean nulls in column X" |
| **Tier 2** | Multi-step or unclear scope | Full lifecycle: workspace_state.md, data-spec.md, analysis_journal.md | "Help me clean this dataset" |
| **Tier 3** | Multi-dataset or cross-session | Everything in Tier 2 + multiple data specs, cross-dataset references | "Process these 5 CSVs into one dataset" |

Tier selection is collaborative — agent proposes, user can override. A user saying "help me clean this CSV" should get useful results quickly, not be asked to set up infrastructure first.

**Step 3:** Choose interaction mode:

| Mode | User Involvement | PAUSE Behavior |
|------|-----------------|----------------|
| **Autonomous** | Minimal — agent decides within guardrails | PAUSE only at synthesis preview gate |
| **Collaborative** | User approves plans, reviews findings | PAUSE at phase transitions and decision points |
| **Guided** | User directs each step | PAUSE before every substantive action |

**Step 4:** Follow the phased workflow with PAUSE gates (Tier 2+):

Phase sequence: **Discover → Plan → Execute → Validate → Deliver**

Phases can loop back but never skip forward. You cannot execute without a plan (even an implicit one). You cannot validate without executing something.

PAUSE gates at phase transitions:
- **Discover → Plan:** Present discovery summary with quality score, findings categorized by severity. Wait for user to confirm direction.
- **Plan → Execute:** Present proposed data spec with processing tasks, approaches, success criteria. Wait for user to confirm or modify.
- **Execute → Validate:** Present execution results with before/after comparison. Wait for user to review.
- **Validate → Deliver:** Present compliance report. Wait for user to approve delivery.

Non-skippable (even with fast-forward):
- Auto-profiling on first data load
- Synthesis preview gate (cost implications)

Users or agents can fast-forward specific phases:
- **User-initiated:** "Skip the profiling pause" → immediate, no confirmation needed
- **Agent-suggested:** "Discovery looks clean, fast-forward to execution?" → requires user confirmation

**Step 5:** Show phase indicators in every response (Tier 2+):

```
[Phase: Discover | Tier 2 | Quality: not yet scored]
[Phase: Plan | Tier 2 | Quality: 72/100 | 3 tasks defined]
```

Do NOT show phase indicators for Tier 1 quick tasks.

**Step 6:** Auto-skill detection — when user message contains a data file path or data-related language:

1. **Check workspace** — if no workspace_state.md exists, use `magic-workspace-init`
2. **Load data** — use `magic-data-loading` skill
3. **Auto-profile** — run `quality_score.py` and `detect_all_issues.py` automatically
4. **Present summary** — data overview with quality score and initial findings
5. **Suggest next steps** — lead with direct guidance, mention slash commands as shortcuts:
   - `/data:findings` — structured findings categorized by severity
   - `/data:propose` — draft a processing plan based on findings
   - `/data:explore` — open interactive exploration mode
   - `/data:status` — show current phase and workspace state

**Step 7:** Present findings after discovery in three categories:

1. **Tasks requiring decision** — Quality issues needing user input (include: type, description, impact, sample values, numbered options, recommendation)
2. **Auto-resolvable** — LOW severity, deterministic fix (agent can execute without approval in collaborative mode)
3. **No action needed** — Expected characteristics, informational

**Step 8:** Track progress proactively:

Update `workspace_state.md` on every phase change:
```markdown
## Current State
- **Phase:** Execute
- **Quality Score:** 72/100 → 88/100 (after cleaning)
- **Dataset:** sales_q4.csv (2,500 rows, 6 columns)
- **Skills Applied:** magic-data-loading, magic-data-profiling, magic-data-cleaning
- **Last Checkpoint:** data/checkpoints/cleaned_sales.csv
- **Pending:** Validation against success criteria
```

Record decisions in `logs/analysis_journal.md`:
```markdown
### Decision: [Brief title]
- **Timestamp:** [ISO 8601]
- **Context:** [What was being decided]
- **Options considered:** [List of options presented]
- **Chosen:** [What the user selected]
- **Rationale:** [Why, if stated]
- **Follow-up:** [Next action triggered]
```

**Step 9:** On validation, produce compliance report (Tier 2+):

```markdown
# Compliance Report

**Spec:** [name] v[version]
**Result:** COMPLIANT | NON-COMPLIANT ([N] failures)

## Quality Gates
| Gate | Target | Actual | Status |
|------|--------|--------|:------:|
| Quality score | >= 85 | 90.09 | PASS |
| Max null rate | <= 5% | 3.2% | PASS |
```

**Step 10:** Handle refinement from any phase:

| Trigger | Response |
|---------|----------|
| Validation failures | Present compliance report, propose fixes, loop to Execute or Plan |
| Unexpected execution results | Pause, analyze, adjust approach or re-Discover |
| New insights during discovery | Update data spec, re-enter Planning |
| Script or code failures | Diagnose, fix or write custom code, resume |
| New data characteristics found | Update Discovery Summary, reassess tasks |

Convergence: If refinement doesn't converge after 3+ attempts, suggest relaxing the target.

**New user onboarding:** If no workspace_state.md exists, briefly introduce the pipeline and invite the user to share a data file. Show once per session.

**Data spec format:** Read the lifecycle SKILL.md for data spec format guidance. The spec lives at `{workspace}/specs/data-spec.md`.

$ARGUMENTS
