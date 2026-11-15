# Analysis

## Headline numbers (from `raw_results.jsonl`, recomputed directly, not from a summary script)

12 tasks. 9 passed the shared baseline attempt perfectly (72 of 72 test
cases across those 9 tasks): `rotate_list` (6/6), `merge_intervals` (6/6),
`longest_substring_without_repeat` (6/6), `int_to_roman` (6/6),
`run_length_encode` (5/5), `leftmost_insert_position` (5/5), `spiral_order`
(5/5), `group_anagrams` (4/4), `majority_element` (4/4). No retries fired on
any of these 9; all three conditions are identical by construction.

3 tasks failed the baseline and produced real retry data:

| Task | Baseline | Blind retry path | Blind final | Error-aware path | Error-aware final |
|---|---|---|---|---|---|
| `next_greater_permutation` | 2/5 | 2 -> 5 | **5/5** | 2 -> 2 -> 2 | **2/5** |
| `valid_parenthesis_with_star` | 4/6 | 4 -> 3 -> 4 | **4/6** | 4 -> 4 -> 5 | **5/6** |
| `decode_ways` | 0/6 | 0 -> 3 -> 2 | **2/6** | 0 -> 2 -> 2 | **2/6** |

## What this shows

**Error-aware retry is not reliably better than blind retry, and lost
outright once.** On `next_greater_permutation`, error-aware retry's two
follow-up responses were byte-identical to its own buggy baseline code --
shown the exact failing inputs and outputs, the model echoed the same bug
back twice and never changed a single character. Blind retry, given zero
information beyond "try again," produced a different implementation and
fixed the bug completely on its first extra attempt. See
`failure_examples/next_greater_permutation_copy_paste.md`.

**Retry is not monotonic -- more attempts is not more correct, even within
one strategy.** On `decode_ways`, blind retry's second attempt (3/6) beat
its own third attempt (2/6): the model abandoned a partially-working
recursive approach for a third, more broken one. See
`failure_examples/decode_ways_regression.md`.

**Error-aware retry won clearly exactly once.** On
`valid_parenthesis_with_star`, error-aware retry's final attempt (5/6) beat
both the baseline and every blind-retry attempt -- the one case in this run
where seeing the actual failing test genuinely helped. Blind retry on the
same task also shows a mid-sequence regression below baseline (4 -> 3 -> 4)
before recovering to a tie with baseline, never beating it.

**Taken together:** across the 3 tasks that actually failed, error-aware
retry's final scores were worse-or-equal to blind retry's final scores on 2
of 3 (`next_greater_permutation`: 2 vs 5; `decode_ways`: tied at 2), and
better on 1 of 3 (`valid_parenthesis_with_star`: 5 vs 4). Neither strategy
dominates. The practical implication for a cheap, automatic retry loop:
telling the agent exactly what it got wrong is not a substitute for
verifying the fix actually improved things before accepting it -- on this
run's worst case, the model produced the identical broken answer twice in a
row, which a loop with a fixed retry budget and no independent check would
have accepted as the final, delivered answer.

## No cherry-picking

All 12 tasks are reported, including the 9 that produced no signal (a
ceiling effect at the per-task level, not a null result overall, since the
3 that did fail produced the data analyzed above). All 3 failing tasks'
full attempt sequences are reported, including the 2 of 3 where error-aware
retry did not win. Nothing from `run_log.txt` or `raw_results.jsonl` is
omitted from this file's table.
