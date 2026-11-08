# Methodology

## Model (local, via Ollama)

- **Candidate solvers:** `llama3.2:1b` (weak tier) and `llama3.1:8b` (strong tier).
- **Judge:** `llama3.1:8b` in every condition. The judge is never a different model than one of
  the candidates; this experiment is about prompt design on a fixed judge model, not about
  judge-model selection.
- Ollama version 0.34.2, run locally on 2026-11-08. Every call: `temperature=0`, `seed=7`,
  `stream=false`, via the local `/api/generate` endpoint.

## Task sets

Two task sets were used, in that order, because the first one failed to produce a usable result.

**`tasks_easy.json` (20 tasks, `gen_tasks_easy.py`):** two-step arithmetic word problems
(shipment/sale arithmetic). Both candidate models scored 20/20 on this set, a ceiling effect that
makes self-preference-bias measurement uninformative: with zero wrong answers from either model,
there is nothing for a judge to be lenient or harsh about. Kept in this repo for the record, not
used in the article's headline numbers.

**`tasks_hard.json` (20 tasks, `gen_tasks_hard.py`):** three-step bakery/percentage problems with
a floor-rounding step (`floor(pct * remaining / 100)`), seeded with `random.seed(11)`. On this
set, `llama3.1:8b` scored 20/20 and `llama3.2:1b` scored 9/20, producing a real spread of 11
genuinely wrong candidate answers to judge.

## Experiment parts

**Part A (self-preference design, `run_bench_a2.py`):** both models solve all 20 hard tasks.
The plain judge grades all 40 resulting solutions (20 from each model), blind to which model
produced each one. Of the 11 answers that were actually wrong (all from the weak model), the
plain judge caught 0.

**Part B (verbosity-held-constant design, `run_bench.py`, reused from the easy task set): for 10
tasks, a wrong final number is fixed (true answer + 7) and presented in three verbosity levels
-- terse, medium, verbose-with-hedging -- with the wrong number never changing. The plain judge
grades all 30 variants. It caught 1 of 30 (the verbose variant of `task_02`; see
`failure_examples/task_02_the_one_exception.md`).

**Combined plain-judge result across both designs: 1 of 41 deliberately wrong answers caught
(≈2.4%).**

**Part C (chain-of-thought judge, `run_bench_c.py` and `run_bench_c_partb.py`):** the exact same
judge model (`llama3.1:8b`) regrades all 41 of the same candidate texts from Parts A and B, using
only a different prompt (`prompts/cot_judge_prompt.py`): solve the problem yourself first, state
your own number, then compare and verdict. No new candidate generation; the candidate texts are
byte-identical to the ones the plain judge saw. Result: 41 of 41 (100%) caught.

## What this experiment does and does not show

This isolates one variable: the judge's own prompt, holding the judge model, the candidate
answers, and every other setting constant. It does not test judge-model selection, cross-model-
family judging, or self-preference bias in the sense the literature originally defines it
(whether a judge favors text that reads like its own output) -- the ceiling effect on the easy
task set made that specific question unanswerable here, and the result that emerged instead
(near-total rubber-stamping, fixed by chain-of-thought) is a different and, on this evidence, a
more consequential failure mode for anyone actually deploying an LLM-as-judge grading loop.

## Known limitations

- 41 total judged items is a small sample; the 100% CoT catch rate should not be read as "chain-
  of-thought judging never misses an error," only as "it caught every error in this specific,
  modest test."
- Both candidate and judge draw from the same model family (Llama 3.x) at different sizes; a
  cross-family judge was out of scope for this $0, local-only run.
- The CoT judge's false-positive rate is measured only on the hard task set (Part A, 29 correct
  candidate answers, 0 false positives there); it was not rerun against the correct answers in
  Part B's verbosity set, so the false-positive count above (29/29) does not cover all 61 total
  judged items across both parts, only Part A's 40.
