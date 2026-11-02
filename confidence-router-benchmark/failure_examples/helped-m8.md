# A genuine save: task m8 (medium, idempotency identification)

**Prompt:** Which of these two function signatures is NOT idempotent-safe to retry blindly on a
network timeout: A) `get_user(user_id)` or B) `create_order(cart_id)`? Answer with just "A" or "B".

**Ground truth:** B (`create_order` can create a duplicate order on a blind retry; `get_user` is a
pure read and safe to retry).

**Cheap model's answer:** `A)` -- wrong, and the inverse of the correct answer, 3 output tokens,
$0.0000264.

**Cheap model's self-reported confidence: 0.** Below threshold, so the router escalated.

**Strong model's answer (on escalation):** `B`, with a correct one-sentence explanation of why a
write operation is unsafe to retry blindly and a read operation is safe. 106 output tokens,
$0.0024108 for this call.

**What this shows:** this is the router working exactly as intended -- a genuinely wrong answer,
correctly flagged as low-confidence, correctly escalated, correctly fixed. It is one of only 3
cases like this in the full 30-task set, against 8 wasted escalations and 11 missed ones. The
mechanism is not useless; it is just uncorrelated enough with actual correctness that it does not
pay for itself here. See `analysis.md` for the full breakdown.
