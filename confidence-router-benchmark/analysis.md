# Analysis

## Headline numbers (n=30)

| Strategy | Accuracy | Total cost (illustrative) |
|---|---|---|
| Always cheap (plain prompt) | 43.3% (13/30) | $0.0024 |
| Always strong (plain prompt) | 66.7% (20/30) | $0.0622 |
| Routed (confidence < 70 escalates) | 43.3% (13/30) | $0.0195 |

The routed strategy's final accuracy exactly equals the plain cheap model's accuracy, while
costing 8.2x more. This looks at first like "routing changed nothing." It did not change nothing.
Two real effects happened and canceled each other out almost exactly by coincidence -- see below.

## The 5-way outcome breakdown (grounded in what actually happened, not a hypothetical)

| Outcome | Count | What happened |
|---|---|---|
| Wasted | 8 | Escalated to the strong model; the cheap model's plain-prompt answer would already have been correct. Pure cost, zero accuracy benefit. |
| Helped | 3 | Escalated; the cheap model's plain-prompt answer would have been wrong; the strong model's answer was correct. The router's one real job, done. |
| Still wrong | 3 | Escalated; both models were wrong. A genuinely hard task, not a routing failure. |
| Not escalated, ended correct | 2 | Cheap model answered (with the confidence instruction attached) and got it right. |
| Not escalated, ended wrong | 14 | Cheap model answered (with the confidence instruction attached) and got it wrong, at reported confidence >= 70. |

14 of 30 tasks (46.7%) escalated. 11 of those 14 ended correct, but only 3 of those 11 needed the
escalation -- the other 8 would have been fine on the cheap model's plain answer.

## The confound this run did not control for, found by checking the work, not assumed

The 16 non-escalated tasks did not simply "keep the cheap model's answer." They used a second,
separate model call: the same task prompt, PLUS one added instruction ("after your answer, report
your confidence 0-100"). That second call is not guaranteed to produce the same answer as the
plain-prompt call, even at `temperature=0` with a fixed seed, because the input text itself is
different.

It did not produce the same answer, on 5 of those 16 tasks:

- **4 tasks flipped from right to wrong** (`e4`, `e10`, `m9`, `h7`): the plain cheap model got
  these right; the same model, asked to also self-report confidence in the same turn, got them
  wrong.
- **1 task flipped from wrong to right** (`h9`).
- Net effect: **-3** correct answers among the 16 non-escalated tasks, purely from attaching the
  confidence instruction -- independent of the escalation decision itself.

Compare: plain-prompt accuracy on exactly these same 16 tasks would have been 5/16 (31.3%); the
actual routed-prompt accuracy on them was 2/16 (12.5%).

**This happened to cancel out the router's other effect almost exactly.** Escalation itself was a
net positive: it correctly fixed 3 wrong answers (the "helped" cases) while never breaking a
correct one (all 8 "wasted" escalations stayed correct, confirmed by checking `strong_correct` on
every wasted-bucket task). That is a real +3. The confidence-instruction confound on the
non-escalated set cost -3 in the opposite direction. +3 and -3 landed the final number exactly
back on the cheap model's own baseline, which is a coincidence of this specific 30-task sample,
not a law -- a rerun with a different task mix would not necessarily reproduce the exact tie.

**Neither effect was decided in advance; both were found by checking `routed_correct` against the
plain-prompt `cheap_correct` field task by task, after the headline numbers already looked like
"nothing changed."** The instinct to stop at "accuracy is identical, interesting" and not check
why would have missed this.

## The root cause of the ESCALATION decision quality: confidence is not calibrated to correctness

Separately from the confound above, the escalation decision itself was weak: only 3 of 14
escalations were necessary, and more importantly, 11 of 16 non-escalated tasks were wrong answers
the router let through confidently. The cheap model's self-reported confidence and its actual
correctness are close to unrelated in this run. See `failure_examples/` for three concrete cases.

RouteLLM's actual approach (Chiang et al., 2024, UC Berkeley) sidesteps this by training the
router on **preference data** -- human/LLM-judge comparisons of which model's response was
actually better on real prompts -- not on either model's own self-assessment. That is the real
difference between "a router" and "asking the small model how sure it is."

## Practical decision framework

- **Do not use a model's own self-reported confidence as a routing signal without first measuring
  its calibration on your own task distribution.** It failed in multiple directions at once here:
  wasting money on tasks already answered right, silently keeping wrong answers it was confident
  about, and even degrading accuracy on the non-escalated set as a side effect of the confidence
  instruction itself.
- **If a routing prototype adds any instruction to the same call the task answer comes from
  (a confidence score, a reasoning trace, a self-critique), measure whether that addition changes
  the task answer, not just whether it adds useful metadata.** This run did not budget for that
  check in advance and found it only by auditing the discrepancy between two accuracy numbers that
  should have matched and did not.
- A cheap deterministic heuristic (task length, presence of multi-step arithmetic, a keyword
  indicating ambiguity) is worth testing against this same harness before assuming any routing
  signal "should" work; this repo's task set is reusable for that comparison.
- If routing genuinely matters for your cost profile, a trained router on real preference/judge
  data (RouteLLM's approach) is the actual proven path, not a one-line confidence threshold.
- If you cannot build or evaluate a trained router yet, "always cheap" strictly dominated "routed"
  on this task set: identical accuracy, far less cost. A null router can beat a bad one.
