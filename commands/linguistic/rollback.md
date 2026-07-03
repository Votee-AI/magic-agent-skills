---
description: Rollback to a prior workspace_state snapshot.
nl_triggers:
  - "rollback"
  - "undo that"
  - "go back to [point]"
routes_to: magic-linguistic-orchestrator (rollback mode)
---

# /linguistic:rollback

Restore `workspace_state.md` from a snapshot in `logs/`. The orchestrator snapshots before every destructive update; this command lists snapshots by timestamp and restores the chosen one.

Snapshot naming: `logs/workspace_state-<ISO-timestamp>.md`.

Rollback never deletes existing data files — only the orchestrator's state pointer changes. Re-run downstream specialists if you need fresh artifacts post-rollback.
