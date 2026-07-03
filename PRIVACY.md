# Privacy Policy

MAGIC Data Agent Skills does **not** collect, transmit, or store any telemetry,
analytics, or usage data.

## What this project is

A collection of skill definitions (SKILL.md) and reference Python scripts.
It is not a running service — it has no server, no daemon, no background process.

## Network calls

Some skill scripts make network calls **only when you invoke them**:

- `inspect_hf_dataset.py` — calls HuggingFace Datasets Server API to inspect dataset metadata
- `connect_database.py` — connects to databases via connection strings you provide
- `batch_synthesize.py` — calls LLM endpoints you configure via MAGIC_LLM_* env vars

All network calls are user-initiated and directed at endpoints you control or configure.
No data is sent to Votee AI or any third party.

## Credentials

Credentials (HF_TOKEN, DATABASE_URL, MAGIC_LLM_API_KEY) are read from environment
variables only. They are never logged, transmitted, or stored by skill scripts.
Scripts include credential-scrubbing regexes for output sanitization.
