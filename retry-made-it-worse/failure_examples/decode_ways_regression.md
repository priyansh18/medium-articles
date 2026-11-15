# decode_ways: blind retry's third attempt was worse than its second

**Baseline (0/6, every test crashed).** An off-by-one in the DP loop bounds:
`for i in range(2, n+1)` indexes `s[i]` where `s` has length `n`, so `i == n`
raises `IndexError: string index out of range` on every single call, before
any logic could even run.

**Blind retry, attempt 2 (3/6) -> attempt 3 (2/6), a regression within the
same condition.** Attempt 2 abandoned the iterative DP entirely for a
memoized recursive version and reached 3/6, still wrong on half the cases but
no longer crashing. Attempt 3 abandoned *that* approach too, for a third,
different recursive version with an incoherent digit-clamping rule
(`if curr_num > 26: curr_num = int(s[i])`, then using `curr_num > 26` again a
few lines later as a branch condition after already clamping it below 26 --
a branch that can now never fire), and scored lower than attempt 2.

Three consecutive attempts, three structurally different implementations,
and the middle one was the best of the three. More retries did not mean
monotonic improvement, even within a single retry strategy.

**Error-aware retry (shown the literal `IndexError: string index out of
range` on all 6 inputs) -> patched the crash, never fixed the logic, then
stalled.** Attempt 2 changed `range(2, n+1)` to `range(2, n)` and `return
dp[n]` to `return dp[n-1]`, which stops the crash but shifts the off-by-one
into a silent wrong-answer bug (2/6). Attempt 3, shown the same failing
tests again, made a cosmetic, behavior-free edit (wrapped the same return
value in a redundant `if dp[n-1] != 0 else 0` ternary) and scored identically
(2/6) -- a retry that did nothing but relabel the same wrong answer.

Error-aware retry's best score on this task (2/6) never reached blind
retry's best score (3/6), even though error-aware retry was the only
condition that ever stopped the crash.
