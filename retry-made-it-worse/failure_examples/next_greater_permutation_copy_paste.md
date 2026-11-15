# next_greater_permutation: error-aware retry returned byte-identical code twice

**Baseline (2/5 passing).** The model's first attempt has a genuine bug in the
suffix-reversal line:

```python
digits[i : ] = digits[i - 1 : : -1]
```

This reverses `digits[0:i]` (the prefix up to and including the pivot), not
the suffix `digits[i:]` that actually needs reversing. Because slice
assignment resizes the list to match the right-hand side's length, this also
silently shrinks the list on some inputs. Example: input `[2, 3, 1]` returns
`[3, 3]` (a 2-element list) instead of the correct `[3, 1, 2]`.

Failing tests: `[1, 1, 5]` -> got `[1, 5, 5, 1]`, expected `[1, 5, 1]`.
`[2, 3, 1]` -> got `[3, 3]`, expected `[3, 1, 2]`.

**Blind retry (same prompt, no feedback) -> 5/5, fully fixed on the first
extra attempt.** The model generated a different implementation from scratch
(iterative, correct suffix slice `digits[i+1:] = digits[i+1:][::-1]`) and it
passed every test.

**Error-aware retry (shown the exact two failing inputs and outputs,
explicitly asked to fix the function) -> 2/5, no improvement across 2 extra
attempts.** Both follow-up responses returned the *exact same, byte-identical,
still-buggy function* as the baseline, including the same docstring, same
comments, same bug. The model echoed its own broken code back verbatim twice
in a row, despite being told precisely which two inputs it got wrong and what
it returned versus what was expected.

This is the clearest single data point in this experiment for "giving the
model its own error does not reliably help it fix the error" -- here it did
not help at all, while the "no-information" condition (just ask again) fixed
the bug completely on the first retry.
