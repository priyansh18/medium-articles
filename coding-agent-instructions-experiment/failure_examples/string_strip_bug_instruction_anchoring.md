# Failure: both instruction conditions reproduced the buggy code's core logic

**Task:** `string_strip_bug` — write `clean_username(name)` to lowercase a username and strip
only leading/trailing whitespace, not internal spaces.

**Buggy code shown to the model in every condition:**
```python
def clean_username(name):
    return name.lower().replace(' ', '')
```

**No instructions (pass):**
```python
def clean_username(name):
    return name.lower().strip()
```
A clean rewrite. No trace of the buggy version's `.replace()` approach.

**Concise instructions (fail):**
```python
def clean_username(name):
    return name.strip().lower().replace(' ', '')
```

**Long verbose instructions (fail), byte-identical to the concise failure:**
```python
def clean_username(name):
    return name.strip().lower().replace(' ', '')
```

Both instructed conditions added a `.strip()` call but kept the original `.replace(' ', '')`,
which strips every space in the string instead of just the edges. Neither `instructions_concise.md`
nor `instructions_long.md` mentions this bug family (string method mixups aren't on either
pitfall list). The instructed model did not get confused by a rule that misled it: it produced a
near-identical patch on top of the existing buggy line, while the uninstructed model ignored the
existing approach entirely and wrote a correct one from scratch.

**pytest output (both instructed conditions):**
```
AssertionError: assert 'bobsmith' == 'bob smith'
1 failed, 1 passed in 0.01s
```

One task out of fourteen. Not proof instructions reliably cause this. A real, inspectable
instance of it happening, worth reading the diff for rather than just the pass/fail count.
