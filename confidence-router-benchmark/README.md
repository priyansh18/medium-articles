# Confidence-Based LLM Router Benchmark

A small, local, $0, fully reproducible benchmark testing the routing strategy most people reach
for first when they want to cut LLM cost: ask the cheap model to answer, have it self-report a
confidence score, and escalate to a stronger model when confidence is low.

**Result: on this 30-task set, the routed strategy matched the cheap model's own accuracy exactly
(43.3%) while costing 8.2x more than never routing at all.** Full writeup: [link added on publish].

See `methodology.md` for the exact setup and `analysis.md` for the full breakdown of what the
router got right and wrong, task by task.

## Files

- `tasks.py` -- the 30 tasks (10 easy / 10 medium / 10 hard), each with a programmatic correctness
  check (no subjective grading).
- `run_bench.py` -- runs all three conditions (always-cheap, always-strong, routed) against a local
  Ollama server and writes `raw_results.jsonl` + `summary.json`.
- `make_charts.py` -- regenerates both article charts from the saved results (PIL only).
- `raw_results.jsonl` -- one row per task: every answer, token count, latency, cost and the
  escalation decision.
- `summary.json` -- aggregated accuracy/cost/escalation numbers.
- `failure_examples/` -- three annotated cases: a wasted escalation, a confidently-wrong answer
  that should have escalated and didn't, and a case the router actually fixed.
- `methodology.md` -- models, versions, pricing sources, routing rule, reproduction steps.
- `analysis.md` -- the 5-way outcome breakdown (wasted / helped / still wrong / missed / fine) and
  what it implies for building a router this way.

## Reproduce it

```
ollama pull llama3.2:1b
ollama pull llama3.1:8b
python3 run_bench.py
python3 make_charts.py
```

Deterministic: `temperature=0`, `seed=7` on every call. A clean re-run should reproduce every
number in this repo exactly (confirmed once during this project, see `analysis.md`).

## License

MIT, see `LICENSE`.
