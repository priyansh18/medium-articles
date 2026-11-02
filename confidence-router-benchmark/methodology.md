# Methodology

## Models (local, via Ollama)

- **Cheap tier:** `llama3.2:1b`, Q8_0 quantization, 1.2B parameters.
- **Strong tier:** `llama3.1:8b`, Q4_K_M quantization, 8.0B parameters.
- Ollama version 0.34.2, Python 3.14.7, macOS, run on 2026-10-18.
- Every call: `temperature=0`, `seed=7`, `stream=false`, via the local `/api/generate` endpoint.

These two local models are a size-tier proxy for the "cheap API model vs. frontier API model"
decision a real agent harness makes. They are not DeepSeek V4.1 Flash or GPT-5.6 Sol; this repo
does not claim to reproduce those models' actual accuracy gap. What it reproduces is the
*routing mechanism* -- ask a smaller/cheaper model to self-report confidence, escalate on low
confidence -- which is model-size-agnostic.

## Illustrative cost pricing

Local Ollama execution itself costs $0. To make the accuracy/cost tradeoff concrete, this repo
maps the real token counts Ollama reports for each call onto real, independently-verified
published hosted API pricing as of 2026-10-18:

- Cheap tier: DeepSeek V4.1 Flash, $0.30 / $1.20 per million input/output tokens (DeepSeek's own
  API price, cross-checked against infrabase.ai's pricing tracker).
- Strong tier: GPT-5.6 Sol, $4.00 / $20.00 per million input/output tokens (two independent
  pricing trackers, usagepricing.com and benchlm.ai, agree on this figure; a third source quoted
  $5/$30 and was not used since it could not be corroborated).

This is a cost **proxy**, not a real invoice -- it exists to make the accuracy/cost tradeoff
legible in dollar terms instead of raw token counts.

## Tasks

30 tasks, 10 each at easy / medium / hard, covering the kind of decisions a production agent
harness routes constantly: lookups, unit conversion, log-field extraction, cost arithmetic,
multi-step word problems, subtle code-bug identification, and multi-constraint reasoning with a
distractor. Every task has a `check()` function doing exact or substring matching against a
ground-truth answer -- no subjective grading, no LLM-as-judge in the loop.

## The routing rule under test

This is deliberately the **first, simplest** router someone would reach for, not RouteLLM's
actual approach (see the published article for that contrast):

1. Ask the cheap model the task, plus one extra instruction: report a confidence score 0-100 on
   its own last line.
2. Parse the confidence. If it is missing or below 70, escalate: ask the strong model the
   original task (no confidence instruction) and use its answer.
3. Otherwise, use the cheap model's answer.

Cost for an escalated task = cheap model's confidence-call cost + strong model's cost. Cost for a
non-escalated task = cheap model's confidence-call cost only.

## Reproduction, done once already

This exact setup was re-run once during the project (same seed, same temperature) specifically to
check determinism before publishing. Every accuracy number reproduced exactly; dollar costs
changed only because the strong-tier price was corrected (see `README.md`/article for the
correction). See `analysis.md` for the full breakdown.
