# LLM-Judge Rubber-Stamp Benchmark

A small, local, $0, fully reproducible test of the most common LLM-as-judge grading pattern:
show a judge model a problem and a candidate's final answer, and ask it to say correct or
incorrect, without asking it to solve the problem itself.

**Result: the same judge model (`llama3.1:8b`) caught 1 of 41 deliberately wrong answers (2.4%)
with a plain one-shot grading prompt, and 41 of 41 (100%) once the prompt was changed to make it
solve the problem itself first, then compare.** Full writeup: [link added on publish].

See `methodology.md` for the exact setup and `analysis.md` for the full breakdown, including why
the originally planned self-preference/verbosity-bias framing didn't hold up and what finding
replaced it.

## Files

- `gen_tasks_easy.py` / `tasks_easy.json` -- 20 two-step arithmetic tasks. Produced a ceiling
  effect (both models 20/20); kept for the record, not used in the headline numbers.
- `gen_tasks_hard.py` / `tasks_hard.json` -- 20 three-step bakery/percentage tasks with a
  floor-rounding step, seeded (`random.seed(11)`) to produce a real accuracy spread between the
  two candidate models.
- `run_bench.py` -- Part A (easy-task self-preference design) and Part B (verbosity-held-constant
  design), both against the plain judge prompt.
- `run_bench_a2.py` -- reruns the Part A design on the harder task set.
- `run_bench_c.py` / `run_bench_c_partb.py` -- reruns the chain-of-thought judge prompt over the
  same candidate texts from Parts A and B, no new generation calls.
- `raw_results_easy_and_verbosity.jsonl`, `raw_results_parta_hard.jsonl`,
  `raw_results_cot_judge.jsonl`, `raw_results_cot_judge_partb.jsonl` -- full raw output of every
  run above.
- `prompts/` -- the exact three prompt templates used: `solve_prompt.py`, `judge_prompt.py`
  (plain), `cot_judge_prompt.py` (chain-of-thought).
- `failure_examples/` -- two annotated cases: the clearest plain-judge rubber-stamp failure
  (`htask_01`), and the one exception where the plain judge did catch a wrong answer (`task_02`).
- `charts/` -- the article's results chart (`results-chart.png`) and the script that built it
  (`gen_chart.py`, PIL only, no matplotlib dependency).
- `methodology.md` -- models, task design, both experimental parts, and known limitations.
- `analysis.md` -- the full numeric breakdown and why the original framing changed mid-experiment.

## Reproduce it

```
ollama pull llama3.2:1b
ollama pull llama3.1:8b
python3 gen_tasks_easy.py
python3 gen_tasks_hard.py
python3 run_bench.py
python3 run_bench_a2.py
python3 run_bench_c.py
python3 run_bench_c_partb.py
python3 charts/gen_chart.py
```

Deterministic: `temperature=0`, `seed=7` on every solver/judge call; task generation seeded
(`random.seed(7)` easy, `random.seed(11)` hard). A clean re-run should reproduce every number in
this repo.

## License

MIT, see `LICENSE`.
