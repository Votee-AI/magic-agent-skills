<!-- Natural Language Triggers: "let me explore this data", "investigate this", "what's in this dataset?", "what patterns do you see?", "look into this data", "explore database", "explore db schema" -->

Enter data explore mode — an interactive thinking partner for investigating data.

Read the `magic-data-exploration` SKILL.md and follow its stance and instructions.

**On entry:**
1. Read workspace_state.md, analysis_journal.md, latest checkpoint, and existing reports
2. **Detect data source type:**
   - If workspace has a database connection (Data Source type = database): read `magic-data-exploration` SKILL.md `## Database Exploration` section, start with schema discovery
   - If workspace has file data: proceed with standard file exploration
   - If no data loaded yet: ask user what to explore
3. Auto-run surface profiling with `quality_score.py` (profiling skill, Tier A scriptable — call directly) if data hasn't been profiled yet. Then use exploration scriptable tools: `detect_patterns.py` (Tier A), `segment_analysis.py` (Tier A), `relationship_explorer.py` (Tier A), `prepare_for_exploration.py` (Tier A)
4. Present a summary of what's known about the data
5. Ask "What would you like to explore?"

**Stance:** Curious, visual, adaptive, patient, grounded. Read-only — no data modifications.

$ARGUMENTS
