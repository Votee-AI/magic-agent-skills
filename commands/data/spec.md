<!-- Natural Language Triggers: "create a spec", "what's the processing plan?", "show the data spec", "update the spec", "evaluate against spec" -->

Manage the workspace data spec for the current data project.

Read the `magic-data-lifecycle` SKILL.md for the full data spec format and lifecycle context.

**Actions (based on arguments or current state):**

- **No arguments + no spec exists:** Infer a data spec from discovery results. Run discovery scripts if needed, draft `specs/data-spec.md`, present to user for approval.
- **No arguments + spec exists:** Show current spec status — processing tasks, success criteria, completion progress.
- **"evaluate" or "check":** Run validation against the spec's success criteria. Produce a compliance report.
- **"refine" or "update":** Update the spec based on new findings, user feedback, or changed requirements. Record changes in Refinement History.

**This triggers Tier 2+ lifecycle.** Creating or managing a data spec implies full lifecycle tracking.

$ARGUMENTS
