<!-- Natural Language Triggers: "undo that", "go back to the previous version", "rollback", "revert to checkpoint", "that made things worse" -->
# /data:rollback — Revert to Previous Checkpoint

Roll back to a previous data checkpoint when a processing step produces undesirable results.

## Workflow

### Step 1: List Available Checkpoints

List all checkpoint files in `data/checkpoints/` with timestamps and row counts:

```
Available checkpoints:
  1. ckpt_01_loaded.csv      — 2026-03-09 14:23 — 52,311 rows
  2. ckpt_02_profiled.json   — 2026-03-09 14:25 — (metadata only)
  3. ckpt_03_cleaned.csv     — 2026-03-09 15:01 — 51,842 rows
  4. ckpt_04_transformed.csv — 2026-03-09 15:30 — 51,842 rows
```

### Step 2: Accept Target or Ask

If the user specified a checkpoint (e.g., `/data:rollback ckpt_03`), use that. Otherwise, ask which checkpoint to revert to.

### Step 3: Confirm Before Reverting

Always confirm before reverting:

> Reverting to **ckpt_03_cleaned.csv** (51,842 rows, from 2026-03-09 15:01).
> This will set the active working data back to the post-cleaning state.
> Newer checkpoints (ckpt_04_transformed.csv) will be kept but no longer active.
>
> Proceed? (yes/no)

### Step 4: Execute Rollback

1. Copy the target checkpoint to the active working location
2. Update `workspace_state.md` with the rollback event and new current state
3. Record the rollback in `logs/analysis_journal.md`:
   ```markdown
   ### Rollback
   - **Timestamp:** [ISO 8601]
   - **Reverted to:** [checkpoint name]
   - **Reason:** [user's stated reason or "user requested"]
   - **Newer checkpoints preserved:** [list]
   ```
4. Confirm completion: "Rolled back to [checkpoint]. Newer checkpoints preserved — you can re-apply them if needed."

## Constraints

- **NEVER delete newer checkpoints** — they may be needed later. Rollback only changes which checkpoint is "active", not the checkpoint history.
- **Always confirm** before executing the rollback.
- **Always record** the rollback in the analysis journal.
- **If no checkpoints exist**, inform the user: "No checkpoints found. Run a data processing step first to create checkpoints."
