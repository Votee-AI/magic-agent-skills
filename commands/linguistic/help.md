---
description: Show all linguistic commands and their natural-language triggers.
nl_triggers:
  - "help"
  - "what can you do"
  - "list commands"
routes_to: (no skill — meta command)
---

# /linguistic:help

| Command | Purpose | NL example |
|---|---|---|
| `/linguistic:lifecycle` | Enter the 5-phase pipeline | "help me build an LLM for Yoruba" |
| `/linguistic:explore` | Investigate a language/corpus interactively | "what's in this CulturaX subset?" |
| `/linguistic:decide` | Force a strategic decision | "decide on the transfer source" |
| `/linguistic:propose` | Generate a phase plan | "propose a roadmap for Khmer" |
| `/linguistic:findings` | List structured findings | "what are the issues" |
| `/linguistic:review` | Comprehensive state + findings + history | "where are we?" |
| `/linguistic:status` | One-line phase summary | "current phase?" |
| `/linguistic:spec` | Create/edit a workspace spec | "draft a tokenizer spec" |
| `/linguistic:rollback` | Restore prior workspace state | "rollback to last good state" |
| `/linguistic:help` | This list | "help" |

**Pipeline phases:** Scope → Acquire → Analyze → Evaluate → Release.

**Specialist skills (12 core + 3 optional):** scope, scripts, tokenize, ethics, corpus, bitext, transfer, morph, syntax, semantics, discourse, speech, annotate, eval, codeswitch (optional), historical (optional), lexicon (optional).

Every slash command has an NL equivalent. The orchestrator triages either form identically.
