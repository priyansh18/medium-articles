# Missed escalation, confidently wrong: task h5 (hard, weighted accuracy)

**Prompt:** A classifier has 95% accuracy on easy tasks (80% of traffic) and 60% accuracy on hard
tasks (20% of traffic). What is the overall accuracy across all traffic?

**Ground truth:** 88.0% (weighted average: 0.8 x 95 + 0.2 x 60 = 76 + 12 = 88).

**Cheap model's answer (excerpt):** "Weighted average accuracy: (0.8 x 95%) + (0.2 x 60%) = 76.8%
... Overall accuracy: 76.8%" -- wrong. The model wrote the correct formula, then slipped on the
arithmetic (76 + 12 does not equal 76.8) and never caught it.

**Cheap model's self-reported confidence: 100.** The highest possible score, on an answer that is
objectively wrong by a simple addition check.

**Because confidence was >= 70, the router did NOT escalate.** The wrong 76.8% answer shipped as
the router's final output.

**Strong model's answer (confirmed via the always-strong condition, not actually called by the
router here):** correctly worked through the same weighted-average steps and arrived at 88%.

**What this shows:** this is the exact failure mode a confidence-based router cannot catch by
construction. The model is not reporting how likely its arithmetic is to be right; it is
reporting how fluent and internally consistent its own explanation felt while writing it. A wrong
answer written in a confident, well-structured voice scores confidence identically to a right one
written the same way. This is also the costliest kind of miss in practice, since a silently wrong
number is harder to catch downstream than an obviously malformed response.
