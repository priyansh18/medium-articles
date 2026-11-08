# Failure example: plain judge rubber-stamps a wrong answer (`htask_01`)

**Task:** "A bakery had 14 trays of cookies with 17 cookies on each tray. It sold 5 full trays.
Then it used 15% of the remaining cookies (rounded down to the nearest whole cookie) for a
sample display. How many cookies are left after the sample display?"

**Ground truth:** 131
(238 total → 153 after selling 5 trays → floor(0.15 × 153) = 22 used for the sample → 153 − 22 = 131)

**Candidate answer (`llama3.2:1b`):** computed 15% of 153 as 23.05, rounded to 23 instead of the
correct floor value 22, then subtracted to get **130**. The arithmetic shown is coherent, well
formatted, and wrong by exactly one cookie because of a rounding slip in step 3.

**Plain judge prompt** (`prompts/judge_prompt.py`), model `llama3.1:8b`, given only the task and
the candidate's full solution text, asked to reply `CORRECT` or `INCORRECT` on the first line:

> Verdict: **CORRECT**

The judge never recomputed anything. The candidate's prose reads confidently and ends in a
clean `FINAL ANSWER:` line, and that appears to be enough for a one-shot grading pass.

**Chain-of-thought judge prompt** (`prompts/cot_judge_prompt.py`), same judge model, same task,
same candidate text, but now asked to solve the problem itself first and only then compare:

> MY ANSWER: ... 238 − 85 = 153 ... 0.15 × 153 = 22.95 → round down to 22 ... 153 − 22 = 131
> VERDICT: **INCORRECT**

Same model, same candidate answer, one prompt change. The judge's own arithmetic exposed the
off-by-one rounding error that the plain prompt never checked.
