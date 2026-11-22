# Coding Agent Instructions Experiment

A small, local, mostly-$0, fully reproducible test of whether a repository instruction file
(like `CLAUDE.md` or `AGENTS.md`) changes a coding agent's pass rate on small bug-fix tasks, and
whether making that file longer and more thorough changes the answer.

**Result: with no instructions, the model fixed 14 of 14 bugs. With a concise (~10-line)
instruction file, 13 of 14. With a long, verbose (~150-line) instruction file covering the same
substance, also 13 of 14. Both instructed conditions failed the same task, in the same way:
reproducing the original buggy function's flawed logic almost unchanged instead of writing a
correct fix from scratch.** Full writeup: [link added on publish].

See `methodology.md` for the exact setup and `analysis.md` for the full numeric breakdown.

## Files

- `tasks.py` / `tasks.csv` -- 14 small Python bug-fix tasks (off-by-one, mutable default
  argument, wrong exception type, unstable sort, accidental mutation, missing dict default, wrong
  recursion base case, string-method mixup, missing empty-input guard, wrong boolean condition,
  off-by-one slice, broken accumulator, and others), each with its own pytest file.
- `sanity_check.py` -- confirms every task's buggy code genuinely fails its own test before any
  model is involved.
- `instructions_concise.md` -- the ~10-line repo conventions file.
- `instructions_long.md` -- the ~150-line "Repository Engineering Standards" file, same substance
  as the concise file, wrapped in philosophy and process sections.
- `llm_client.py` -- the free-tier provider fallback used (Gemini -> Groq -> Ollama).
- `run_experiment.py` -- runs all 14 tasks x 3 conditions, one completion each, grades every
  response by actually running pytest in an isolated subprocess. Writes `raw_results.jsonl`
  incrementally (one line per trial) and `run_log.txt`.
- `raw_results.jsonl`, `run_log.txt` -- full raw output of the run analyzed in the article.
- `prompts/` -- the exact prompt sent for the `none` and `concise` conditions on one example task.
- `configs/run_config.json` -- run parameters, including the real provider mix used.
- `failure_examples/` -- the one task that failed under both instructed conditions, with the full
  response diff against the uninstructed pass.
- `charts/` -- the article's results chart (`pass-rate-by-condition.png`) and the script that
  built it (`gen_chart.py`, PIL only, no matplotlib dependency, no AI image generator).
- `analysis.md` -- the full numeric breakdown and what it does and does not show.
- `requirements.lock.txt` -- pinned dependency versions for this run.

## Reproduce it

```
ollama pull llama3.1:8b
ollama serve
python3 sanity_check.py        # confirms all 14 bugs are real
python3 run_experiment.py      # writes raw_results.jsonl + run_log.txt
python3 charts/gen_chart.py    # regenerates the chart from raw_results.jsonl
```

Not deterministic: `llama3.1:8b` runs at Ollama's default settings, no seed pinned. A fresh run
will not reproduce these exact numbers; it is expected to reproduce the general pattern (most
tasks solved cleanly regardless of instructions, occasional cases where instructions visibly
change the model's relationship to the existing buggy code).

## License

MIT, see `LICENSE`.
