# /data:deliver — Deliver processed data to a destination

## Usage

`/data:deliver [destination]`

## Description

Deliver your processed data to an external destination. This command guides you through the delivery workflow with appropriate safety checks.

## Destinations

### Database (`db`)

<!-- Natural Language Triggers: "deliver to database", "write to database", "save to db", "export to database" -->

Deliver processed data to a database table.

Read the `magic-data-transformation` SKILL.md `## Database Delivery` section for delivery guidance.

**Workflow:**
1. Check workspace state for current data (latest checkpoint or DataFrame)
2. Ask user for delivery target:
   - Environment variable for connection (default: `DATABASE_URL`)
   - Target table name
   - Write mode: append (default) / replace
3. Validate data with `validate_transform.py` (transformation skill, Tier A scriptable — call directly) before delivery
4. Present write plan: row count, target table, mode, column mapping
5. **PAUSE (always):** Confirm before writing — "Write {N} rows to {table}? [y/N]"
6. Execute write via `deliver_to_db.py`
7. Update `workspace_state.md` with delivery results

**Safety:** This command creates a NON-read-only connection. The PAUSE gate is mandatory and cannot be skipped even in autonomous mode.

### HuggingFace Hub (`hf`)

Upload processed data to a HuggingFace dataset repository.

**Workflow:**
1. Confirm repo name and visibility (private by default)
2. Generate dataset card from data metadata
3. Upload data folder with atomic commit
4. Report Hub URL

**Example:**
```
/data:deliver hf
```

**Required:** `HF_TOKEN` env var or `huggingface-cli login`

**Scripts used:**
- `generate_dataset_card.py` (loading skill, callable tool) — creates README.md with schema and provenance
- `deliver_to_hf.py` (transformation skill, callable tool) — uploads folder to HF Hub (has built-in confirmation prompt)

### Local File (`local`)

Save processed data to a local output directory (default behavior without destination).

**Example:**
```
/data:deliver local
```

## Safety

- All external deliveries require user confirmation (PAUSE gate)
- Database writes use non-read-only connections — PAUSE is mandatory
- Defaults to private visibility for HuggingFace repos
- Credentials are never included in uploads or dataset cards
- Use `--create-pr` for PR-based HF delivery when working in teams
