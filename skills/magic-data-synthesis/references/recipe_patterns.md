# Recipe Patterns — When to Use Which Template

## Template Decision Table

| Input shape | Goal | Template |
|---|---|---|
| **Existing data with missing/sentinel values** | Fill/enrich columns (definitions, translations, annotations) | `text_generation_template.py` (local) or `text_generation_gemini_template.py` (cloud) |
| Q&A seed CSV (`question`, `answer`) | Chain-of-thought reasoning traces | `reasoning_trace_template.py` |
| Document/passage seed | Grounded Q&A pairs | `qa_generation_template.py` |
| No seed (sampler-driven) | Open-domain Q&A | `qa_generation_template.py` |
| No seed, task diversity needed | Instruction-following dataset (Alpaca/ShareGPT) | `instruction_tuning_template.py` |
| No seed, code tasks | Python/SQL generation with validation | `code_generation_template.py` |
| Anything else | Custom schema, multi-modal, agent traces, etc. | `custom_recipe_template.py` |

**Quick pick by speed:**
- Fast iteration / CI testing → `text_generation_gemini_template.py` (Gemini, ~2 rec/s)
- Privacy / offline / free → `text_generation_template.py` (local LM Studio, ~0.1 rec/s)

## Template Summaries

### `reasoning_trace_template.py`
**Use for:** Nemotron-style chain-of-thought datasets where an existing Q&A corpus is the seed.

Key columns: seed `question`/`answer` → sampler `difficulty`/`domain` → LLM `reasoning_trace` → LLM `final_answer` → `LLMJudgeColumn` (ReasoningQuality + AnswerCorrectness) → Expression score extractions.

Cost profile: ~3,500 tokens/row combined. Most expensive template — CoT output is verbose.

Pitfalls:
- Use `SamplingStrategy.SHUFFLE` to avoid clustering by seed order.
- Guard judge score extraction: `{{ col.ScoreName.score if col.ScoreName.score is not none else 0 }}`
- Avoid seed column name collisions with sampler columns (`difficulty`, `domain`).

### `qa_generation_template.py`
**Use for:** Generating question-answer pairs from source documents, or open-domain Q&A via samplers.

Context-grounded variant: seed = passages/contexts → LLM `question` → LLM `answer` → judge (Groundedness + Completeness).

Open-domain variant: replace seed with `CategorySampler` for topic/domain, then generate both question and answer.

Cost profile: ~2,000 tokens/row average.

### `instruction_tuning_template.py`
**Use for:** Alpaca/ShareGPT-style `instruction + input + output` triplets with diverse task coverage.

Key technique: `SUBCATEGORY` sampler for coherent domain→task pairings. `BERNOULLI` `has_input` flag controls whether an input field exists per row. Use `{% if has_input == 1 %}` in prompts to conditionalize.

Cost profile: ~2,000 tokens/row average (input column generated for ~60% of rows).

### `code_generation_template.py`
**Use for:** Python or SQL code generation with correctness validation.

Key columns: sampler `industry_sector` → subcategory `topic` → sampler `code_complexity` → LLM `instruction` → `LLMCodeColumn` (strips markdown fences automatically) → `LLMJudgeColumn` (Relevance/Pythonic/Readability/Efficiency) → `ValidationColumn` (ruff linter, zero LLM cost).

Cost profile: ~1,500 tokens/row. `ValidationColumn` has zero LLM cost.

Pitfalls:
- Use `LLMCodeColumnConfig`, not `LLMTextColumnConfig`, for generated code.
- Set `ValidationColumn.batch_size=100` for runs > 1,000 rows (default is 10).
- SQL: use dialect-specific `CodeLang.SQL_SQLITE` / `SQL_POSTGRES`.

### `custom_recipe_template.py`
**Use for:** Any schema that doesn't fit the four above — novel tasks, multi-modal, agent traces, structured JSON output.

Start here when: output is not text/code/Q&A, you need `LLMStructuredColumnConfig` with a Pydantic `output_format`, or you need `@dd.custom_column_generator` for deterministic logic.

Pitfalls:
- `@dd.custom_column_generator` decorator is **mandatory** for `CustomColumnConfig`.
- `side_effect_columns` must be declared in the decorator for any column the generator writes beyond its own name.
- `output_format` takes a **Pydantic class**, not an instance.

## Axes-of-Diversity Mental Model

Every recipe needs variation along at least two axes to produce a useful training set:

1. **Content axis** — what the data is about (seed rows, `CategorySampler`, `SubcategorySampler`)
2. **Style/format axis** — how it is expressed (difficulty, tone, `answer_format_hint`, `PersonSampler`)
3. **Quality axis** — signal for filtering (`LLMJudgeColumn` scores, `ValidationColumn`)

If your recipe only varies on one axis, add a sampler column for a second.

## Column Execution Order

DataDesigner executes columns in DAG order (topological sort, insertion-order tiebreak):

```
SeedDataset columns (auto, no deps)
  → SamplerColumns (no deps)
    → LLMTextColumns (reference seed + sampler outputs)
      → LLMJudgeColumns (reference LLM outputs)
        → ExpressionColumns (extract scores from judge dicts)
          → ValidationColumns (operate on LLM/Code columns)
```

Always define columns in this order. A column can only reference columns defined before it.
