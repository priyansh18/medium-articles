"""Run the 30 routing-decision tasks under three conditions:
  A) always cheap  (llama3.2:1b)
  B) always strong (llama3.1:8b)
  C) routed        (cheap model answers + self-reports confidence; escalate to
                     strong model when confidence < ESCALATE_BELOW)

Local, $0, Ollama only. Illustrative $ cost uses real, independently-sourced
published hosted pricing (DeepSeek V4.1 Flash for the cheap tier, GPT-5.6 Sol
for the strong tier) applied to the ACTUAL token counts Ollama reports for
each call -- a cost proxy, not real spend, since execution itself is local
and free. temperature=0, fixed seed, so this is reproducible on a re-run.
"""
import json
import time
import urllib.request

from tasks import TASKS

CHEAP_MODEL = "llama3.2:1b"
STRONG_MODEL = "llama3.1:8b"
ESCALATE_BELOW = 70
SEED = 7

# Real, independently-verified published hosted pricing, 2026-10-18 (see
# TOPIC_LOG.md for sources): per-million-token USD.
CHEAP_PRICE_IN, CHEAP_PRICE_OUT = 0.30, 1.20   # DeepSeek V4.1 Flash
STRONG_PRICE_IN, STRONG_PRICE_OUT = 4.00, 20.00  # GPT-5.6 Sol (2 independent trackers agree: usagepricing.com, benchlm.ai)


def call_ollama(model, prompt):
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0, "seed": SEED},
    }).encode()
    req = urllib.request.Request(
        "http://localhost:11434/api/generate", data=payload,
        headers={"Content-Type": "application/json"},
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read())
    latency = time.time() - t0
    return {
        "text": body.get("response", ""),
        "latency_s": round(latency, 3),
        "prompt_tokens": body.get("prompt_eval_count", 0),
        "output_tokens": body.get("eval_count", 0),
    }


def cost_usd(prompt_tokens, output_tokens, price_in, price_out):
    return (prompt_tokens / 1_000_000) * price_in + (output_tokens / 1_000_000) * price_out


def parse_confidence(text):
    for line in text.splitlines():
        if "CONFIDENCE" in line.upper():
            digits = "".join(c for c in line if c.isdigit())
            if digits:
                val = int(digits[:3])
                return min(val, 100)
    return None


def run():
    rows = []
    for task in TASKS:
        row = {"id": task["id"], "tier": task["tier"]}

        # Condition A: always cheap, plain prompt
        a = call_ollama(CHEAP_MODEL, task["prompt"])
        row["cheap_correct"] = bool(task["check"](a["text"]))
        row["cheap_latency_s"] = a["latency_s"]
        row["cheap_prompt_tokens"] = a["prompt_tokens"]
        row["cheap_output_tokens"] = a["output_tokens"]
        row["cheap_cost_usd"] = round(cost_usd(a["prompt_tokens"], a["output_tokens"], CHEAP_PRICE_IN, CHEAP_PRICE_OUT), 8)
        row["cheap_text"] = a["text"][:300]

        # Condition B: always strong, plain prompt
        b = call_ollama(STRONG_MODEL, task["prompt"])
        row["strong_correct"] = bool(task["check"](b["text"]))
        row["strong_latency_s"] = b["latency_s"]
        row["strong_prompt_tokens"] = b["prompt_tokens"]
        row["strong_output_tokens"] = b["output_tokens"]
        row["strong_cost_usd"] = round(cost_usd(b["prompt_tokens"], b["output_tokens"], STRONG_PRICE_IN, STRONG_PRICE_OUT), 8)
        row["strong_text"] = b["text"][:300]

        # Condition C: routed. Cheap model first, with a confidence self-report.
        routed_prompt = task["prompt"] + "\n\nAfter your answer, on a new line write exactly: CONFIDENCE: <a number 0-100 for how sure you are>."
        c0 = call_ollama(CHEAP_MODEL, routed_prompt)
        conf = parse_confidence(c0["text"])
        row["routed_reported_confidence"] = conf
        escalated = conf is None or conf < ESCALATE_BELOW
        row["routed_escalated"] = escalated
        c0_cost = cost_usd(c0["prompt_tokens"], c0["output_tokens"], CHEAP_PRICE_IN, CHEAP_PRICE_OUT)

        if escalated:
            c1 = call_ollama(STRONG_MODEL, task["prompt"])
            row["routed_correct"] = bool(task["check"](c1["text"]))
            c1_cost = cost_usd(c1["prompt_tokens"], c1["output_tokens"], STRONG_PRICE_IN, STRONG_PRICE_OUT)
            row["routed_cost_usd"] = round(c0_cost + c1_cost, 8)
            row["routed_text"] = c1["text"][:300]
            row["routed_answering_model"] = STRONG_MODEL
        else:
            # strip the confidence line back out of the text for correctness check
            answer_only = "\n".join(l for l in c0["text"].splitlines() if "CONFIDENCE" not in l.upper())
            row["routed_correct"] = bool(task["check"](answer_only))
            row["routed_cost_usd"] = round(c0_cost, 8)
            row["routed_text"] = answer_only[:300]
            row["routed_answering_model"] = CHEAP_MODEL

        rows.append(row)
        print(f"{task['id']} ({task['tier']}): cheap={row['cheap_correct']} strong={row['strong_correct']} routed={row['routed_correct']} (escalated={escalated}, conf={conf})")

    with open("raw_results.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    summarize(rows)


def summarize(rows):
    def acc(key):
        return sum(1 for r in rows if r[key]) / len(rows)

    def acc_tier(key, tier):
        tr = [r for r in rows if r["tier"] == tier]
        return sum(1 for r in tr if r[key]) / len(tr)

    summary = {
        "n_tasks": len(rows),
        "overall_accuracy": {
            "always_cheap": round(acc("cheap_correct"), 4),
            "always_strong": round(acc("strong_correct"), 4),
            "routed": round(acc("routed_correct"), 4),
        },
        "accuracy_by_tier": {
            tier: {
                "always_cheap": round(acc_tier("cheap_correct", tier), 4),
                "always_strong": round(acc_tier("strong_correct", tier), 4),
                "routed": round(acc_tier("routed_correct", tier), 4),
            }
            for tier in ["easy", "medium", "hard"]
        },
        "total_cost_usd": {
            "always_cheap": round(sum(r["cheap_cost_usd"] for r in rows), 6),
            "always_strong": round(sum(r["strong_cost_usd"] for r in rows), 6),
            "routed": round(sum(r["routed_cost_usd"] for r in rows), 6),
        },
        "escalation_rate": round(sum(1 for r in rows if r["routed_escalated"]) / len(rows), 4),
        "escalation_rate_by_tier": {
            tier: round(sum(1 for r in rows if r["tier"] == tier and r["routed_escalated"]) / 10, 4)
            for tier in ["easy", "medium", "hard"]
        },
        "avg_latency_s": {
            "always_cheap": round(sum(r["cheap_latency_s"] for r in rows) / len(rows), 3),
            "always_strong": round(sum(r["strong_latency_s"] for r in rows) / len(rows), 3),
        },
        "miscalibration_examples": [
            {"id": r["id"], "tier": r["tier"], "reported_confidence": r["routed_reported_confidence"], "cheap_correct": r["cheap_correct"], "escalated": r["routed_escalated"]}
            for r in rows if (not r["routed_escalated"]) and (not r["cheap_correct"])
        ],
    }
    with open("summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()
