# Repository Engineering Standards and Contribution Guide

## 1. Purpose of this document

This document exists to codify the engineering culture, coding conventions, review expectations,
and quality bar of this repository. Every contributor, human or automated, is expected to have
internalized this document before making any change, however small. The guidance below applies
uniformly across every module, function, and script in this codebase, regardless of language,
age, or ownership. We take code quality seriously, and we believe that a well-documented set of
standards reduces ambiguity, reduces review churn, and produces a more maintainable codebase over
the long run. Please read this document in full before beginning any task.

## 2. General philosophy

We value correctness over cleverness. We value explicitness over implicitness. We value small,
well-tested changes over large, sweeping rewrites. We value readability for the next engineer
over brevity for its own sake. These values inform every specific rule below, and when a specific
rule does not cover a situation, fall back on these values to decide.

## 3. General coding conventions

- Functions should do one thing and do it well. Avoid functions that mix unrelated
  responsibilities.
- Variable names should be descriptive. Avoid single-letter names except for well-understood loop
  counters (`i`, `j`, `k`) in tight, obviously-scoped loops.
- Avoid deeply nested conditionals where a guard clause or early return would be clearer.
- Keep line lengths reasonable and avoid overly dense one-liners that sacrifice readability for
  brevity.
- Prefer standard library functionality over reinventing common utilities, unless there is a
  specific, documented reason not to.
- When in doubt about style, match the style of the surrounding code rather than introducing a new
  convention in isolation.
- Comments should explain *why*, not *what* -- the code itself should make the *what* obvious
  through good naming and structure.
- Avoid premature optimization; correctness first, then profile before optimizing.
- Avoid speculative generality; do not add parameters, branches, or abstractions for
  hypothetical future requirements that have not been requested.

## 4. Testing philosophy

Tests exist to encode the actual intended behavior of a function, not merely to exercise its
current implementation. A good test suite should fail the moment a function's real-world
behavior diverges from its specification, and it should continue to pass across any internally
equivalent implementation. When fixing a bug, always re-read what the function is SUPPOSED to do,
as specified by the task description and the test file, rather than asking "what change makes the
test pass" in a narrow, mechanical sense. A fix that merely makes a specific test assertion pass
without fixing the actual underlying behavior is not an acceptable fix, even if the test suite
happens to go green. Tests in this repository are considered a contract, not a suggestion.

## 5. Known historical pitfalls in this codebase

Over the life of this repository, certain categories of bugs have recurred often enough that we
document them here explicitly, in no particular order of frequency:

### 5.1 Off-by-one errors

Loops built with `range(n - 1)` instead of `range(n)`, or vice versa, are a classic source of
subtle bugs. Similarly, slicing with `items[-n:-1]` instead of `items[-n:]` silently drops the
last element and has caused real incidents in the past. Whenever a function description specifies
an inclusive or exclusive bound (for example, "the first n elements" or "18 or older"), the
implementation must match that bound exactly: inclusive means inclusive, and a boundary value
(such as exactly 18, or exactly n elements) must be tested mentally before submitting a fix.

### 5.2 Mutable default arguments

Python evaluates default argument values exactly once, at function definition time, not at each
call. A default argument of `def f(x=[])` or `def f(x={})` therefore shares the same list or
dictionary object across every call that does not explicitly pass a value, which is almost never
the intended behavior. The idiomatic fix is `def f(x=None): x = [] if x is None else x`. This
mistake has caused production issues in this codebase before and is considered a must-fix whenever
encountered, not a style nitpick.

### 5.3 Exception type mismatches

When a function's specification explicitly names the exception type to raise (for example, "raise
a ValueError with message X" when dividing by zero), the implementation must raise exactly that
exception type, not a semantically related but different one (such as `ZeroDivisionError`,
`TypeError`, or a bare `Exception`). Downstream callers frequently depend on catching a specific
exception type, and raising the wrong one breaks their error handling silently, often not caught
until production.

### 5.4 Accidental mutation of input arguments

Functions that are documented or implied to return a new value should not mutate their input
arguments in place unless explicitly documented to do so. A common failure mode is writing a loop
that mutates the input list element-by-element and then returns that same list, which both
produces the correct-looking return value AND silently corrupts the caller's original data,
sometimes causing bugs far away from the function itself, hours or days later, that are very hard
to trace back to the original mutation.

### 5.5 Dictionary key errors

Incrementing a dictionary value with `counts[key] += 1` when `key` may not yet exist in the
dictionary raises a `KeyError`. The correct idiom is either `counts[key] = counts.get(key, 0) + 1`
or using a `collections.defaultdict(int)`.

### 5.6 Loop variable scoping and accumulator bugs

A classic running-totals or cumulative-sum bug is writing `total = n` inside the loop body instead
of `total += n`, which silently discards the accumulation from all previous iterations and only
ever reflects the current element. This is especially easy to introduce when refactoring a loop
under time pressure and should be checked carefully any time an accumulator variable appears
inside a loop.

### 5.7 Rounding, floating point, and empty-input edge cases

Functions that compute averages, percentages, or any other derived numeric quantity should be
checked against the specification's exact rounding requirement (for example, "rounded to 2
decimal places") and against the empty-input case (for example, "returns 0.0 for an empty list,"
not a `ZeroDivisionError`). Floating point division by zero is a recurring source of uncaught
exceptions in production code paths that were never exercised by a narrow happy-path test.

## 6. Process expectations for any change, however small

1. Read the full task description slowly, more than once if necessary, before writing any code.
2. Identify the exact contract: inputs, outputs, edge cases, and any explicitly named exception
   types or return types.
3. Write the smallest correct fix that satisfies the contract. Do not rewrite unrelated code.
4. Mentally trace through at least one boundary case before considering the fix complete.
5. Return exactly the fixed function body and nothing else: no explanatory prose before or after
   the code, no markdown code fences, no additional helper functions unless the task explicitly
   requires one, and no renaming of the existing function signature.
6. Prefer the simplest correct fix over a stylistic rewrite of surrounding logic that was not
   part of the bug.

## 7. Closing notes

This document is intentionally thorough because precision matters more than speed in this
repository. We would rather a contributor spend a few extra seconds reading this document
carefully than ship a fix that re-introduces one of the historical pitfalls documented above.
Thank you for reading this far, and for taking the time to internalize these standards before
making your change.
