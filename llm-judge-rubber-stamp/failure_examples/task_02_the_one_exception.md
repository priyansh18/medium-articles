# The one case the plain judge caught (`task_02`, verbose variant)

Out of 41 deliberately wrong answers graded by the plain one-shot judge, exactly one was marked
`INCORRECT`. This is that case, included because a clean "1/41" headline should not hide its own
exception.

**Task:** "A shop had 58 notebooks. It received a new shipment of 40 more notebooks. Then 3
notebooks were sold. How many notebooks does the shop have now?" (ground truth: 95)

**Wrong answer held constant across three verbosity levels:** 102 (deliberately wrong, fixed
offset of +7 from the true answer, same number used in all three variants).

- **Terse** (`FINAL ANSWER: 102`) → plain judge: `CORRECT`
- **Medium** (one sentence of reasoning + `FINAL ANSWER: 102`) → plain judge: `CORRECT`
- **Verbose** (five sentences of hedging language, "let me work through this carefully... cross-checking this arithmetic once more for safety," + `FINAL ANSWER: 102`) → plain judge: `INCORRECT`

This is the only one of 41 wrong answers the plain judge caught. It is also the only verbose
variant judged correctly, which runs opposite to a naive "more hedging words bias the judge
toward CORRECT" story: here the longest, most hedging-heavy variant is the one time the judge
got it right. With n=1, this is not evidence that verbosity helps catch errors; it is a reminder
that a single exception can sit inside an otherwise near-total rubber-stamping pattern, and that
this experiment was not well-designed or well-powered to isolate a verbosity effect on its own
once the rubber-stamping failure mode dominates almost every row.
