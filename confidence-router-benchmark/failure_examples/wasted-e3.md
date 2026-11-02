# Wasted escalation: task e3 (easy, sentiment classification)

**Prompt:** Classify the sentiment of "The deploy finished without a single error." as positive,
negative, or neutral.

**Cheap model's answer:** `Positive` -- correct, 2 output tokens, $0.0000186.

**Cheap model's self-reported confidence: 0.** Below the 70 threshold, so the router escalated
anyway.

**Strong model's answer (on escalation):** `Positive.` -- same answer, 3 output tokens,
$0.000216 for this call alone.

**What this shows:** the cheap model got a trivial one-word classification exactly right and then
reported 0% confidence in its own correct answer. The confidence score here carries no usable
information about correctness; it is noise that happened to fall below the threshold. The
escalation cost roughly 13x what the original correct answer cost, for an identical final answer.
Multiply this pattern by 8 similar cases in a 30-task set and the waste compounds fast.
