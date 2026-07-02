<!-- Natural Language Triggers: "what did we find?", "show me the findings", "what issues are there?", "summarize the problems", "what needs to be fixed?" -->

Present current analysis findings interactively as structured, actionable proposals.

**Steps:**
1. Read available analysis outputs from `logs/` directory:
   - `quality_score.py` output (overall quality score and grade)
   - `detect_all_issues.py` output (issue inventory)
   - `deep_quality_analysis.py` output (anomaly flags, investigation hints)
   - `content_validator.py` output (sentinel and content validation)
2. Categorize findings into three groups:
   - **Tasks requiring decision** — Quality issues or processing opportunities needing user input
   - **Auto-resolvable** — Low-severity items fixable deterministically
   - **No action needed** — Expected data characteristics
3. Present each decision task with concrete numbers, sample values, numbered options, and a recommended approach
4. Wait for user to choose which tasks to pursue
5. Record decisions in `logs/analysis_journal.md`
6. Route to the appropriate skill (cleaning, synthesis, transformation, validation) based on user choices

The agent composes the findings presentation directly from script outputs.

$ARGUMENTS
