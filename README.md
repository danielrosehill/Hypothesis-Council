# Hypothesis-Council

A variant of [karpathy/llm-council](https://github.com/karpathy/llm-council) adapted for **hypothesis testing**.

You submit a prediction or claim. A small council of deliberately-diverse LLMs — each grounded with fresh web context — independently scores the likelihood and hunts for counterarguments. A synthesiser merges the verdicts into a Typst report.

## The council

Picked for lineage diversity, not size:

| Slot | Model | Why |
|------|-------|-----|
| 1 | `anthropic/claude-sonnet-4.5` | Strong reasoning, measured |
| 2 | `x-ai/grok-4` | Different training culture, tends to push back |
| 3 | `minimax/minimax-m2` | Non-Western lineage, different priors |

All routed via **OpenRouter**.

## Grounding

Light context injection via **Tavily search** (not deep research) — the council needs enough to know what the hypothesis refers to, not a full literature review. Each member sees the same grounding pack to keep scoring comparable.

## Council bias

Members are prompted as **skeptical falsifiers**, not cheerleaders. Their job is to:
1. Score the hypothesis likelihood (0–100)
2. State calibrated confidence
3. Enumerate the strongest counterarguments and failure modes
4. Flag what evidence *would* change their mind

## Output

A Typst report in `reports/` with:
- The hypothesis and grounding summary
- Per-member score + rationale + top counterarguments
- Consensus band + divergence analysis (where they disagreed and why)
- Ranked counterargument list
- Evidence appendix with citations

## Usage

```bash
export OPENROUTER_API_KEY=...
export TAVILY_API_KEY=...

python -m council "Iran will resume overt uranium enrichment above 60% within 6 months"
```

## Status

Scaffold. Not yet wired.
