# Methodology: does retrying a coding agent's failed attempt help or hurt?

**Model:** `llama3.1:8b`, served locally via Ollama (`http://localhost:11434/api/generate`),
default temperature 0.7, no system prompt. $0 cost, no API calls, no paid
service of any kind.

**Design: shared baseline, three branches.** Every task gets exactly ONE
first attempt (the "baseline"). If the baseline already passes every test,
all three conditions are recorded as that single passing result and no
retries fire (this happened on 9 of the 12 tasks). If the baseline fails at
least one test, the SAME baseline attempt branches into three independently
tracked conditions:
- **No retry:** the baseline score is the final score. No further calls.
- **Blind retry:** the exact same prompt is sent again, with zero information
  about what failed, up to 2 extra times (stops early if a perfect score is
  reached).
- **Error-aware retry:** the model's own previous code is shown back to it,
  along with a specific, auto-generated list of which test inputs failed and
  what the function returned versus what was expected (see
  `prompts/error_aware_followup_template.py`), up to 2 extra times.

Sharing one baseline across all three conditions (rather than three
independent first attempts) holds the starting point constant, so a
difference in final score is attributable to the retry condition, not to
attempt-to-attempt randomness in the first try.

**Tasks (12 total, `tasks.py`):** classic algorithmic interview problems
(next permutation, Roman numeral conversion, decode-ways DP, valid
parenthesis with wildcards, spiral matrix traversal, etc), each with 4-6
test inputs chosen to include at least one edge case. An earlier, easier
task set (ordinary list/string utilities: palindrome check, median, rotate,
caesar cipher, etc) produced a ceiling effect -- 11 of 12 tasks solved
perfectly on the first attempt by this model, leaving no failure data to
study retries on. That easier set is not included in these results; this
repo's `tasks.py` is the harder replacement set that actually produced
failures to analyze. This mirrors a documented lesson from an earlier
article in this series (`llm-judge-rubber-stamp/`): an easy-task ceiling
effect is a design flaw, caught and fixed by hardening the task set, not
reported as a null result.

**Grading (`grade.py`):** each candidate function is extracted from the
model's raw response (first fenced Python code block, or the raw text if
none), written to an isolated temp directory, and run in a `python3 -I`
subprocess (no access to the current directory or its modules) against each
test input, with a 15-second timeout. Output is compared against a
hand-verified reference implementation (`reference_solutions.py`) for the
same inputs; a result counts as a pass only if the value matches exactly
(or the expected exception type is raised).

**Reference implementations are the grading oracle.** Each one in
`reference_solutions.py` was independently sanity-checked against known
values (e.g. `int_to_roman(1994) == "MCMXCIV"`, `decode_ways("11106") == 2`,
`valid_parenthesis_with_star("(*))") == True`) before being trusted, since an
error there would silently mis-grade every model response for that task.

**What this is not:** a benchmark of `llama3.1:8b`'s general coding ability,
or a claim that these results generalize to other models, other task
difficulties, or other retry-prompt designs. It is one model, one set of 12
tasks, one specific error-aware-retry prompt template, run once each (no
repeated trials per condition). The honest scope is: on this run, with this
model, these specific retries did not reliably help, and in one case made
no difference across 2 extra attempts while the no-feedback condition fixed
the same bug on its first retry.
