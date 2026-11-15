"""The exact follow-up prompt template used for the error-aware retry
condition (see run_experiment.py:failure_detail_text / run_one). The failing
test detail is generated automatically from the grading harness's own
per-test results, never hand-written per task."""

FOLLOWUP_TEMPLATE = (
    "Here is a Python function you wrote:\n\n```python\n{cur_code}\n```\n\n"
    "It fails these test cases:\n{detail}\n\n"
    "Fix the function so it passes all of them. Return only the corrected "
    "function, no example usage, no explanation."
)

# `{detail}` is built by failure_detail_text(): one line per failing test,
# e.g.:
#   - Input (([1, 1, 5],)): expected [1, 5, 1], but got [5, 1, 1] expected [1, 5, 1]
#   - Input ('(((*)',): expected it to raise ValueError, but did not raise, returned False
