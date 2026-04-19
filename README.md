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

## Grading axes

Each member independently scores on three **independent** 0.0–1.0 axes:

- **Conspiratorial** — how much hidden coordination / actors-against-stated-interests the theory requires. High ≠ bad; some true theories are conspiratorial.
- **Credible** — internal coherence and factual consistency, independent of probability.
- **Likely** — the member's actual probability estimate.

Plus per member: supporting evidence, refuting evidence, load-bearing assumptions, what-would-shift-me, and — critically — an **alternative read**: their own best explanation of what's actually happening, so the user isn't just told "unlikely" but shown a competing narrative.

## Demo run

See [`examples/demo-run/`](examples/demo-run/) for a full council evaluation of a theory about the current Israel-Iran war dynamics ([input](examples/iran-war-theory.txt)).

Council consensus: high-conspiratorial (0.85 mean), low-credible (0.32), low-likely (0.13). All three members converged independently on the same alternative explanation — pragmatic multi-party de-escalation driven by Gulf-state pressure and Iranian assurances, rather than a coordinated US-Iran ruse.

The interesting part isn't that the theory was rated unlikely — it's that three models from three different lineages (Anthropic, xAI, MiniMax) produced structurally similar counter-narratives, which is some evidence the alternative read isn't just one model's bias.

## Reports

| Run | Report |
|-----|--------|
| 2026-04-18 21:43:36 | [reports/2026-04-18_214336/report.pdf](reports/2026-04-18_214336/report.pdf) |
| 2026-04-18 21:46:45 | [reports/2026-04-18_214645/report.pdf](reports/2026-04-18_214645/report.pdf) |
| demo-run | [examples/demo-run/report.pdf](examples/demo-run/report.pdf) |
