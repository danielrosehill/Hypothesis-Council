---
name: start-hypothesis-council
description: Launch a Hypothesis-Council run to evaluate a prediction or claim via three deliberately-diverse LLMs (Sonnet, Grok, MiniMax) with Tavily-grounded context. Use when the user says "score this hypothesis", "evaluate this prediction", "red-team this claim", "/start-hypothesis-council", or provides a prediction/claim in the Hypothesis-Council repo. Gathers the hypothesis, optional grounding hints, runs the council with skeptical-falsifier prompting, and surfaces the consensus band, counterarguments, and Typst report.
---

# Start a Hypothesis Council

You are operating inside the `Hypothesis-Council` repo. This skill runs a hypothesis-evaluation session.

## Preconditions

1. Repo root must contain `council/` (the package) and the entry point `python -m council`. If not, the user is outside the repo.
2. Check env: `OPENROUTER_API_KEY` and `TAVILY_API_KEY` must both be set. Tell the user exactly which is missing; do not invent values.
3. `uv sync` if the venv is missing.

## Step 1 — Capture the hypothesis

Ask for a **single crisp claim or prediction**, ideally in under one sentence. Good shape:

- "Iran will resume overt uranium enrichment above 60% within 6 months."
- "By end of 2027, >40% of new passenger cars sold in Israel will be EVs."
- "The Fed will cut rates at least twice before the end of H1 2027."

Bad shape: sprawling essays, multi-clause "and" statements. If the user gives one, ask them to pick the single most load-bearing claim, or split into multiple runs.

## Step 2 — Clarify grounding (optional)

If the hypothesis is niche or time-sensitive, ask whether the user wants to pass specific grounding hints (additional search queries, URLs). Otherwise Tavily default grounding is used.

## Step 3 — Run the council

```bash
python -m council "<the hypothesis in quotes>"
```

Tell the user:
- Three members are deliberating (Sonnet, Grok, MiniMax via OpenRouter).
- Each scores on three axes: Conspiratorial / Credible / Likely.
- Tavily is pulling light grounding context — this is *not* a deep research run.

## Step 4 — Surface the output

When complete:

1. Show the **consensus band** (agreement or divergence across the three).
2. Show each member's Likely score and top counterarguments.
3. Read out the **alternative reads** — each member's best competing narrative. This is the most useful output for most users.
4. Report the Typst PDF path in `reports/`.

If the three members disagree sharply, flag that — high divergence is itself signal.

## Step 5 — Iterate

Offer to:

- Re-run with a sharpened hypothesis.
- Probe a specific counterargument by running a derived hypothesis (e.g., flip the polarity, narrow the time horizon).

## Failure modes

- Missing keys → stop, explain, no workarounds.
- Tavily quota exhausted → fall back to ungrounded council if the user approves, else abort.
- A single member errors → report which one; offer to retry or proceed with the remaining two (flag the reduced diversity).

## Out of scope

- This skill does not forecast markets or make recommendations. It scores a claim and surfaces counterarguments; the user does the acting.
- Not to be confused with the decision-framework council (`LLM-Council-Decide`). This one is about **truth / likelihood of a claim**, not about **which option to pick**.
