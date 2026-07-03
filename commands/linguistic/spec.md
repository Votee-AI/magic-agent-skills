---
description: Create or edit a workspace data/model spec under specs/.
nl_triggers:
  - "draft a spec"
  - "write a model card"
  - "spec out [task]"
routes_to: magic-linguistic-orchestrator → relevant specialist
---

# /linguistic:spec

Create or edit a structured spec document for the current workspace under `specs/`. Common spec types:

| Spec | Owner skill | Purpose |
|---|---|---|
| `language-spec.md` | magic-linguistic-scope | Language identity, typology, resource class, vitality |
| `data-spec.md` | magic-linguistic-corpus + magic-linguistic-bitext | Data manifest with sources, licenses, sizes, dedup stats |
| `tokenizer-spec.md` | magic-linguistic-tokenize | Tokenizer config, fertility audit, vocab extension plan |
| `eval-spec.md` | magic-linguistic-eval | Benchmark choice, metric choice, contamination assessment |
| `model-card.md` | magic-linguistic-ethics | Public-facing model card with intended uses, limits, attribution |

Specs are user-editable and reviewed before phase advancement.
