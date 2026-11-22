# Methodology: do repository instruction files actually help a coding agent fix bugs?

**Model:** Google Gemini (free tier), accessed via a local `generate_text(prompt,
provider="auto")` fallback wrapper. Groq was the preferred first provider but its configured
model endpoint returned HTTP 404 on every call during this run (the model name appears to have
been retired server-side); the wrapper fell through to Gemini automatically, so every trial in
this run was actually served by Gemini, not Groq. $0 cost, free-tier API calls only.

**Design: one shared task set, three independent conditions, one completion each.** 14 small,
self-contained Python bug-fix tasks (`tasks.py`), each a short buggy function plus a pytest file
that fails on the bug and passes on the real fix (verified by `sanity_check.py` before the run:
all 14 bugs are genuinely caught by their own tests). Each task is sent to the model exactly once
under each of three conditions, for 42 total completions:

- **None:** just the task description and buggy code, no repo instructions of any kind.
- **Concise:** a ~10-line `instructions_concise.md` prepended to the prompt — covers output
  format, and the three bug families actually present in the task set (off-by-one, mutable
  defaults, wrong exception type), in plain bullet points.
- **Long verbose:** a ~150-line `instructions_long.md` prepended to the prompt — a fictional
  "Repository Engineering Standards" document covering the SAME substance as the concise file
  (all the same pitfalls, slightly expanded to cover all bug families in the task set, not just
  three), but wrapped in philosophy, testing-ethos, and process sections modeled on an
  over-stuffed real-world `CLAUDE.md`/`AGENTS.md`.

Each condition is otherwise identical: same task, same buggy code, same "return only the fixed
function" instruction at the end of the prompt.

**Grading (`run_experiment.py`):** the model's response is parsed for a fenced Python code block
(falling back to raw text if none is present), written to an isolated temp directory, and run
against that task's real pytest file in a `python3 -m pytest` subprocess with a 20-second
timeout. A trial counts as a pass only if pytest exits 0. No LLM self-grading, no reading
responses by eye.

**What this is not:** a benchmark of Gemini's general coding ability, or a claim that these
results generalize to other models, other instruction files, or other task difficulties. It is
one model family, one set of 14 small bug-fix tasks, one specific concise file, one specific long
file, run once per task per condition (no repeated trials per cell). The honest scope is: on this
run, with this model, this is what prepending these two specific instruction files did to pass
rate on these 14 tasks — nothing stronger.

**No cherry-picking:** the result reported in the article is whatever this run's real numbers
show, including if the pattern is flat, counter to the pitched hook, or inconclusive given the
sample size.
