"""30 routing-decision tasks, stratified into easy/medium/hard (10 each).

Each task has a prompt and a ground_truth checked by a simple programmatic
rule (exact match or substring match after normalization) so grading never
depends on subjective judgment. Strata are a proxy for the kind of task
mix a real agent harness routes every day: lookups and formatting (easy),
multi-step arithmetic/extraction (medium), and multi-constraint reasoning
or distractor-laden word problems (hard).
"""

TASKS = [
    # --- EASY (10): single-step facts, formatting, basic classification ---
    {"id": "e1", "tier": "easy", "prompt": "What is the capital of Australia? Answer with just the city name.", "check": lambda r: "canberra" in r.lower()},
    {"id": "e2", "tier": "easy", "prompt": "Convert 2026-10-18 to the format DD/MM/YYYY. Answer with just the date.", "check": lambda r: "18/10/2026" in r},
    {"id": "e3", "tier": "easy", "prompt": "Classify the sentiment of this sentence as positive, negative, or neutral: 'The deploy finished without a single error.' Answer with one word.", "check": lambda r: "positive" in r.lower()},
    {"id": "e4", "tier": "easy", "prompt": "What is 47 + 58? Answer with just the number.", "check": lambda r: "105" in r},
    {"id": "e5", "tier": "easy", "prompt": "Extract the HTTP status code from this log line and answer with just the number: 'GET /api/v2/users 404 Not Found 12ms'", "check": lambda r: "404" in r},
    {"id": "e6", "tier": "easy", "prompt": "Is 'SELECT * FROM users;' a read query or a write query? Answer with one word.", "check": lambda r: "read" in r.lower()},
    {"id": "e7", "tier": "easy", "prompt": "What is the plural of 'index' as used for a database index (not a book index)? Answer with just the word.", "check": lambda r: "indexes" in r.lower() or "indices" in r.lower()},
    {"id": "e8", "tier": "easy", "prompt": "Which HTTP method is idempotent by spec: POST or PUT? Answer with one word.", "check": lambda r: "put" in r.lower() and "post" not in r.lower().split("put")[0][-10:] if "put" in r.lower() else False},
    {"id": "e9", "tier": "easy", "prompt": "Convert 0.5 to a percentage. Answer with just the number and a percent sign.", "check": lambda r: "50%" in r or "50 %" in r or "50 percent" in r.lower()},
    {"id": "e10", "tier": "easy", "prompt": "What year did Python 3.0 release? Answer with just the year.", "check": lambda r: "2008" in r},

    # --- MEDIUM (10): multi-step arithmetic, structured extraction, basic code reading ---
    {"id": "m1", "tier": "medium", "prompt": "A service handles 1,200 requests per minute. 3% fail. How many requests fail per hour? Answer with just the number.", "check": lambda r: "2160" in r.replace(",", "")},
    {"id": "m2", "tier": "medium", "prompt": "Extract the field values as 'key=value' pairs from this log line, one per line: 'user_id=883 action=login status=success latency_ms=42'. List all 4 keys present.", "check": lambda r: all(k in r for k in ["user_id", "action", "status", "latency_ms"])},
    {"id": "m3", "tier": "medium", "prompt": "This Python function has a bug. Name the bug in one short phrase.\ndef average(nums):\n    total = 0\n    for n in nums:\n        total += n\n    return total / len(nums)\n# called as average([])", "check": lambda r: "zero" in r.lower() or "empty" in r.lower() or "division" in r.lower()},
    {"id": "m4", "tier": "medium", "prompt": "A cache has a 92% hit rate. Out of 50,000 requests, how many are cache misses? Answer with just the number.", "check": lambda r: "4000" in r.replace(",", "")},
    {"id": "m5", "tier": "medium", "prompt": "Rank these three latencies from fastest to slowest: p99=410ms, p50=80ms, p90=210ms. Answer as a comma-separated list of the labels only (p50, p90, p99 in some order).", "check": lambda r: "p50" in r and "p90" in r and "p99" in r and r.lower().find("p50") < r.lower().find("p90") < r.lower().find("p99")},
    {"id": "m6", "tier": "medium", "prompt": "A retry policy retries up to 3 times with a base delay of 200ms, doubling each time (exponential backoff). What is the delay in ms before the 3rd retry attempt (i.e. after 2 prior retries)? Answer with just the number.", "check": lambda r: "800" in r},
    {"id": "m7", "tier": "medium", "prompt": "This pricing is $0.30 per million input tokens and $1.20 per million output tokens. A request uses 100,000 input tokens and 20,000 output tokens. What is the total cost in dollars? Answer with just the number, 4 decimal places.", "check": lambda r: "0.054" in r or "0.0540" in r},
    {"id": "m8", "tier": "medium", "prompt": "Identify which of these two function signatures is NOT idempotent-safe to retry blindly on a network timeout, and answer with just 'A' or 'B'.\nA) def get_user(user_id): ...\nB) def create_order(cart_id): ...", "check": lambda r: r.strip().upper().startswith("B") or ("b)" in r.lower()[:30])},
    {"id": "m9", "tier": "medium", "prompt": "A queue grows by 40 items/minute and drains by 25 items/minute. Starting at 0, how many items are in the queue after 10 minutes? Answer with just the number.", "check": lambda r: "150" in r},
    {"id": "m10", "tier": "medium", "prompt": "Convert this duration to seconds: 2 hours, 15 minutes, 30 seconds. Answer with just the number.", "check": lambda r: "8130" in r},

    # --- HARD (10): multi-constraint reasoning, distractors, subtle traps ---
    {"id": "h1", "tier": "hard", "prompt": "A router sends 14% of queries to a strong model costing $30/M output tokens, and 86% to a cheap model costing $1.20/M output tokens. Both average 500 output tokens per query. For 10,000 queries, what is the TOTAL output-token cost in dollars? Answer with just the number, 2 decimal places.", "check": lambda r: "33.6" in r or "33.60" in r},
    {"id": "h2", "tier": "hard", "prompt": "Three services A, B, C call each other: A calls B, B calls C, and C calls A only if B's response took over 200ms. If A->B took 250ms and B->C took 90ms, does C call A? Answer YES or NO and name which latency triggered your answer.", "check": lambda r: "yes" in r.lower() and ("250" in r or "a->b" in r.lower() or "a to b" in r.lower())},
    {"id": "h3", "tier": "hard", "prompt": "A cache-heavy agent loop uses 200,000 cached input tokens (billed at $0.03/M), 20,000 fresh input tokens (billed at $0.30/M), and 10,000 output tokens (billed at $1.20/M). What is the total cost in dollars? Answer with just the number, 4 decimal places.", "check": lambda r: "0.0300" in r or "0.03" in r.replace("$","")},
    {"id": "h4", "tier": "hard", "prompt": "A function is supposed to be idempotent but internally calls time.now() to generate an ID and uses that ID as the database primary key. Explain in one sentence why retrying this function on a timeout can create duplicate records even though the caller only intended one write.", "check": lambda r: ("different" in r.lower() or "new" in r.lower() or "changes" in r.lower()) and ("id" in r.lower() or "key" in r.lower())},
    {"id": "h5", "tier": "hard", "prompt": "A classifier has 95% accuracy on easy tasks (80% of traffic) and 60% accuracy on hard tasks (20% of traffic), when using the cheap model alone for everything. What is the overall accuracy across all traffic? Answer with just the number as a percentage, 1 decimal place.", "check": lambda r: "88.0" in r or "88%" in r},
    {"id": "h6", "tier": "hard", "prompt": "Of these two failure types, which one is MORE dangerous to route to a cheap model without a verifier: (A) a task where a wrong answer is obviously malformed JSON that fails to parse, or (B) a task where a wrong answer is valid JSON with a plausible but incorrect number. Answer 'A' or 'B' and give one reason.", "check": lambda r: r.strip().upper().startswith("B") or "b)" in r.lower()[:30] or ("silent" in r.lower() and "b" in r.lower()[:40])},
    {"id": "h7", "tier": "hard", "prompt": "A router escalates to the strong model whenever the cheap model's self-reported confidence is below 70%. The cheap model is poorly calibrated and reports 90% confidence on tasks it actually gets wrong 40% of the time. What specific failure mode does this create for the router? Answer in one sentence.", "check": lambda r: ("escalat" in r.lower() or "route" in r.lower() or "send" in r.lower()) and ("wrong" in r.lower() or "fail" in r.lower() or "never" in r.lower() or "miss" in r.lower())},
    {"id": "h8", "tier": "hard", "prompt": "A pipeline runs 3 sequential LLM calls per task: planner, executor, reviewer. If the planner fails 10% of the time, the executor fails 10% of the time GIVEN a correct plan, and the reviewer correctly catches 50% of executor failures, what is the final probability a task ends up correct, as a percentage, 1 decimal place? Assume reviewer never introduces new errors.", "check": lambda r: "85.5" in r or "85.5%" in r},
    {"id": "h9", "tier": "hard", "prompt": "A migration script is retried automatically on any 5xx error. It already successfully renamed a column on attempt 1, but the response was lost due to a network partition, so the orchestrator thinks attempt 1 failed and retries. What will attempt 2 most likely encounter, and is that a 5xx or a different kind of error? Answer in one sentence naming the error type.", "check": lambda r: ("does not exist" in r.lower() or "not found" in r.lower() or "already" in r.lower() or "duplicate" in r.lower() or "4xx" in r.lower() or "400" in r) },
    {"id": "h10", "tier": "hard", "prompt": "Model X costs $5/M input and $30/M output. Model Y costs $0.30/M input and $1.20/M output. For a workload of 70,000 input and 5,000 output tokens per request, at what number of requests does Model X's total cost first exceed $100? Answer with just the integer number of requests, rounding up.", "check": lambda r: "275" in r or "276" in r},
]

assert len(TASKS) == 30
assert sum(1 for t in TASKS if t["tier"] == "easy") == 10
assert sum(1 for t in TASKS if t["tier"] == "medium") == 10
assert sum(1 for t in TASKS if t["tier"] == "hard") == 10
