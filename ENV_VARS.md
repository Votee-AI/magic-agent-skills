# Environment Variables

The authoritative reference for every environment variable read by MAGIC Agent Skills —
the **CLI installer** (`cli/`), the **synthesis engine**, and the **skills**. Copy
[`.env.example`](.env.example) to `.env` and fill in what you need; everything here is
optional unless marked **Required**.

> **No secrets in this file or in `.env.example`** — only names, purposes, and defaults.
> Put real keys in your local `.env` (git-ignored) or your shell environment.

## CLI installer

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `MAGIC_REPO` | No | `Votee-AI/magic-agent-skills` | **Repo override for the installer.** The CLI fetches skills from GitHub at install time; set this to `owner/name` to install from a fork or mirror instead of the default repo (read in `cli/src/core/fetch.ts`; validated against the GitHub `owner/name` charset). |

## CI / engine gating

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `MAGIC_REQUIRE_ENGINE` | No | unset | **Hard-fail gate for the synthesis engine.** When set to `1`, the synthesis engine MUST be importable or the run/test fails loudly (no silent skip). CI's `engine-integration` job sets `MAGIC_REQUIRE_ENGINE=1` so a missing/broken DataDesigner engine fails the build instead of being skipped. Leave unset locally to allow graceful skip when the optional engine isn't installed. |
| `MPLBACKEND` | No | `Agg` (recommended for headless/CI) | Matplotlib backend. Set to `Agg` for headless or CI runs (any skill that renders charts); the test suite expects `MPLBACKEND=Agg`. |

## Synthesis engine — LLM configuration

Used by `magic-data-synthesis` (the DataDesigner-backed engine). Configure the model
endpoint your synthesis runs should use.

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `MAGIC_LLM_MODEL` | No | engine default | Model name/id for synthesis (e.g. a local model id or a hosted model). |
| `MAGIC_LLM_BASE_URL` | No | provider default | OpenAI-compatible base URL (e.g. `http://localhost:1234/v1` for a local server). |
| `MAGIC_LLM_API_KEY` | No | — | API key for the configured LLM endpoint (use a placeholder like `local` for keyless local servers). |
| `MAGIC_LLM_PROVIDER` | No | engine default | Provider hint (e.g. `local`, `openai`, `gemini`) when the engine needs it to route. |
| `MAGIC_LLM_MAX_TOKENS` | No | engine default | Max output tokens per generation. Use ≥ 2048 for reasoning models (they emit hidden reasoning before the answer). |
| `MAGIC_LLM_SEED` | No | — | Deterministic sampling seed where the provider supports it. Note: some providers reject a `seed` parameter — leave unset if you hit a 400. |
| `DATA_DESIGNER_ASYNC_ENGINE` | No | `1` (async DAG engine on) | Set to `0` to force the synchronous engine for deterministic ordering; otherwise the v0.6 async DAG engine with adaptive (AIMD) concurrency is used. |

## Provider API keys (set the one(s) your model endpoint needs)

| Variable | Required | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | No | OpenAI / OpenAI-compatible providers. |
| `GOOGLE_API_KEY` | No | Google Gemini models. |
| `ANTHROPIC_API_KEY` | No | Anthropic Claude models. |
| `NVIDIA_API_KEY` | No | NVIDIA-hosted model endpoints. |

## Data sources

| Variable | Required | Purpose |
|---|---|---|
| `HF_TOKEN` | No | HuggingFace Hub token (for private datasets / gated models). |
| `DATABASE_URL` | No | SQLAlchemy connection string for database-backed loading (PostgreSQL/MySQL/SQLite). |

> **Advanced / template-specific variables.** Individual advanced synthesis templates may
> read additional `MAGIC_*` variables for their specific pipeline knobs; those are
> documented inline in the template they belong to. The variables above cover the engine,
> CLI, and general skills — the public surface.

## Reconciliation

`ENV_VARS.md` and [`.env.example`](.env.example) are kept in sync. `MAGIC_REPO` and
`MAGIC_REQUIRE_ENGINE` are documented here **and** present in `.env.example`.

```bash
grep -q MAGIC_REPO .env.example && grep -q MAGIC_REQUIRE_ENGINE .env.example && echo "in sync"
```
