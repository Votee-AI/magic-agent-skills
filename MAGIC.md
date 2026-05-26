# MAGIC Namespace

**MAGIC** (Multi-Agent Generic Intelligence Capabilities) is a framework for the data work behind LLM development — turning AI coding assistants into specialists for data preparation, synthesis, annotation, tokenizer auditing, evaluation, and everything else needed to build training datasets and extend models to new languages.

This repository is the unified home for all MAGIC agent skills. Each skill suite targets a different stage of the LLM development pipeline.

## Skill Suites

### Data Science (12 skills)

Skills prefixed with `magic-data-*` and `magic-*` cover the core data pipeline: loading, profiling, cleaning, transformation, validation, synthesis, visualization, statistical analysis, and reporting. These are the building blocks for preparing training data — from raw ingestion through quality-gated delivery to HuggingFace, databases, or file formats.

| Skill | Purpose |
|-------|---------|
| `magic-workspace-init` | Workspace scaffolding, environment verification |
| `magic-data-lifecycle` | Multi-skill orchestration, routing, quality gating |
| `magic-data-loading` | Multi-format file detection, auto-encoding, databases, HuggingFace |
| `magic-data-profiling` | Quality scoring, distribution analysis, outlier detection |
| `magic-data-cleaning` | Missing values, normalization, deduplication |
| `magic-data-validation` | Schema inference, constraint checking |
| `magic-data-exploration` | Pattern discovery, segment analysis |
| `magic-data-transformation` | Reshape, aggregate, merge, derive columns |
| `magic-data-synthesis` | LLM-based generation via DataDesigner |
| `magic-statistical-analysis` | Descriptive stats, hypothesis testing |
| `magic-data-visualization` | Chart selection and generation |
| `magic-report-generation` | Structured report assembly |

### Computational Linguistics (18 skills)

Skills prefixed with `linguistic-*` cover low-resource language NLP — essential for extending LLMs beyond high-resource languages. Covers tokenizer auditing, corpus building, morphological analysis, annotation, cross-lingual transfer, evaluation, and more.

| Skill | Purpose |
|-------|---------|
| `linguistic-orchestrator` | Routes tasks to the appropriate linguistic skill |
| `linguistic-scope` | Language assessment, resource classification |
| `linguistic-tokenize` | Tokenizer fertility audit, vocab extension strategy |
| `linguistic-corpus` | Corpus collection and curation |
| `linguistic-morph` | Morphological analysis and generation |
| `linguistic-syntax` | Syntactic parsing, treebanks |
| `linguistic-semantics` | Word embeddings, semantic similarity |
| `linguistic-lexicon` | Lexicon building and management |
| `linguistic-annotate` | Annotation project design, IAA metrics |
| `linguistic-bitext` | Parallel corpus alignment |
| `linguistic-codeswitch` | Code-switching detection and handling |
| `linguistic-discourse` | Discourse analysis and coherence |
| `linguistic-ethics` | Ethical considerations for language technology |
| `linguistic-eval` | Evaluation methodology and benchmarks |
| `linguistic-historical` | Historical linguistics and language change |
| `linguistic-scripts` | Writing system analysis and conversion |
| `linguistic-speech` | Speech processing and phonology |
| `linguistic-transfer` | Cross-lingual transfer and adaptation |

## Shared Utilities

`skills/_linguistic_shared/` contains Python utilities shared across linguistic skills (Unicode inventory, IPA distance calculations). This is not a skill — it has no SKILL.md and is excluded from manifests.

## How Skills Work

Each skill is a self-contained knowledge package in `skills/{name}/`:

```
skills/magic-data-cleaning/
├── SKILL.md          # Frontmatter (metadata) + knowledge document
├── scripts/          # Reference Python implementations
└── references/       # Additional reference material (optional)
```

1. Agent reads `SKILL.md` frontmatter to understand what the skill does
2. Agent reads the knowledge document for domain expertise and procedures
3. Agent optionally reads `scripts/` for reference implementations
4. Agent writes its own code adapted to the specific task

Skills provide knowledge and patterns. The agent decides how to act.

## Schema

All SKILL.md frontmatter follows the [agentskills.io](https://agentskills.io) specification:

- **Root fields:** `name`, `description`, `license`, `compatibility` (spec-defined)
- **Metadata:** Domain-specific extensions under `metadata` (MAGIC extensions)
- **Validation:** `schema/SKILL.schema.json` enforces the format in CI
