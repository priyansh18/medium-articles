# Retry Made It Worse

A small, local, $0, fully reproducible test of the most common cheap "self-correction" pattern
for coding agents: when a candidate function fails its tests, retry it, either blind (try again,
no context) or error-aware (show the model its own code plus exactly which tests failed and why).

**Result: on the 3 of 12 tasks that actually failed the baseline, error-aware retry's final score
was worse than or tied with blind retry's final score on 2 of 3, and better on 1 of 3. On one task,
error-aware retry's two follow-up attempts were byte-identical to its own buggy baseline code.**
Full writeup: [link added on publish].

See `methodology.md` for the exact setup and `analysis.md` for the full numeric breakdown.

## Files

- `tasks.py` -- 12 algorithmic coding tasks (next permutation, decode-ways DP, valid parenthesis
  with wildcards, spiral matrix traversal, and others), 4-6 test inputs each.
- `reference_solutions.py` -- hand-verified ground-truth implementation per task, used as the
  grading oracle.
- `grade.py` -- extracts the candidate function from a model response, runs it in an isolated
  `python3 -I` subprocess per test input with a 15-second timeout, compares against the reference.
- `ollama_client.py` -- thin wrapper around the local Ollama HTTP API (`llama3.1:8b`, default
  temperature 0.7, no system prompt).
- `run_experiment.py` -- the shared-baseline, three-branch design (no retry / blind retry /
  error-aware retry, up to 2 extra attempts per branch). Writes `raw_results.jsonl` and
  `run_log.txt`.
- `raw_results.jsonl`, `run_log.txt` -- full raw output of the run analyzed in this article.
- `prompts/error_aware_followup_template.py` -- the exact follow-up prompt template used for the
  error-aware condition, plus an example of the auto-generated failure detail.
- `failure_examples/` -- two annotated cases: `next_greater_permutation_copy_paste.md` (the
  byte-identical-retry failure) and `decode_ways_regression.md` (the non-monotonic-retry failure).
- `charts/` -- the article's results chart (`results-chart.png`) and the script that built it
  (`gen_chart.py`, PIL only, no matplotlib dependency).
- `methodology.md` -- model, design, task set (including the earlier-ceiling-effect lesson that
  led to this harder task set), and known limitations.
- `analysis.md` -- the full numeric breakdown and what it does and does not show.

## Reproduce it

```
ollama pull llama3.1:8b
python3 run_experiment.py
python3 charts/gen_chart.py
```

Not deterministic: `llama3.1:8b` runs at Ollama's default temperature (0.7), no seed pinned. A
fresh run will not reproduce these exact numbers; it is expected to reproduce the general pattern
(most tasks solved on the baseline, a minority that fail and show mixed retry behavior).

## License

MIT, see `LICENSE`.
