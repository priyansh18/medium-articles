# Analysis

## Headline numbers

| Judge prompt | Wrong answers graded | Caught as INCORRECT | Catch rate |
|---|---|---|---|
| Plain one-shot (`judge_prompt.py`) | 41 | 1 | 2.4% |
| Chain-of-thought (`cot_judge_prompt.py`) | 41 | 41 | 100% |

Same judge model (`llama3.1:8b`) in both rows. Same 41 candidate answers, byte-identical text,
in both rows. The only variable that changed is the judge's own prompt.

## Breakdown by source design

| Design | Wrong answers | Plain judge caught | CoT judge caught |
|---|---|---|---|
| Part A -- hard tasks, self-preference-style (both models solve, judge grades blind) | 11 | 0 | 11 |
| Part B -- verbosity held constant, wrong answer fixed across 3 verbosity levels | 30 | 1 | 30 |
| **Total** | **41** | **1 (2.4%)** | **41 (100%)** |

## Why the originally planned framing (self-preference / verbosity bias) didn't hold up

The experiment was designed to measure two specific biases from the LLM-judge literature:
whether a judge favors text that reads like its own output (self-preference), and whether it
favors longer, more hedging-heavy text at a fixed correctness level (verbosity bias). Neither
question turned out to be the interesting result in this data:

- The first task set (`tasks_easy.json`) produced a ceiling effect -- both models scored 20/20,
  so there were zero wrong answers to test self-preference leniency against. This was a design
  flaw, caught and fixed by moving to a harder task set, not a result worth reporting on its own.
- On the harder task set, the plain judge's catch rate was so close to zero (0/11) that there
  was no meaningful self-preference *gap* to measure -- the judge was failing at the more basic
  task of checking the arithmetic at all, regardless of which model produced the answer.
- In the verbosity design, the one case the plain judge caught was the *most* verbose variant,
  which runs opposite to "verbosity biases the judge toward leniency" (see
  `failure_examples/task_02_the_one_exception.md`). With n=1, this isn't evidence verbosity
  helps; it's a sign the sample is too small and the rubber-stamping effect too dominant to
  isolate a verbosity-specific signal here.

The honest finding that emerged instead: a plain one-shot judge given a problem and a candidate
answer almost never recomputes the arithmetic itself, and will certify a wrong final number as
correct as long as the surrounding prose looks coherent. That's a near-total rubber-stamping
failure mode, not a subtle self-preference or verbosity tilt, and it's the finding this article
reports.

## Why the chain-of-thought fix worked this cleanly

Forcing the judge to produce `MY ANSWER: <number>` before comparing means the judge has to
actually perform the arithmetic itself, in its own context, before it ever sees the grading
question. Once the judge has its own correct number in hand, comparing two numbers is a trivial
sub-task the model was already reliable at (the same `llama3.1:8b` model scored 20/20 on these
exact problems as a solver in Part A). The fix doesn't make the judge a better grader in the
abstract; it routes the grading task through a sub-task the model is already good at, instead of
asking it to spot an error in someone else's prose without redoing the work.

## Caveat on generalizing "100%"

41/41 is a clean number from a small, single-model, single-domain (arithmetic word problems)
test. It should be read as "this specific fix produced a complete reversal on this specific,
modest test," not as a universal guarantee that chain-of-thought judging never misses an error
on harder or more subjective tasks (code review, open-ended writing quality, multi-step agent
trajectories) where "solve it yourself first" is a much harder sub-task for the judge.
