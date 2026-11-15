"""Job 20, article 10 experiment: does retrying a coding agent's failed
attempt help, or can it make things worse? One shared first attempt per
task (the baseline), then two retry strategies branch from the SAME failing
baseline: blind retry (same prompt again, no feedback) vs error-aware retry
(the real test failure fed back). $0, local Ollama llama3.1:8b only.
"""
import json
import sys
import time

sys.path.insert(0, ".")
from tasks import TASKS
from reference_solutions import REFS
from grade import extract_code, grade
import ollama_client

MAX_EXTRA_ATTEMPTS = 2  # on top of the shared baseline attempt
RESULTS_PATH = "../results/raw_results.jsonl"
LOG_PATH = "../results/run_log.txt"

def log(msg):
    print(msg)
    with open(LOG_PATH, "a") as f:
        f.write(msg + "\n")

def expected_for(func, test_inputs):
    fn = REFS[func]
    out = []
    for args in test_inputs:
        try:
            v = fn(*args)
            out.append(("value", v))
        except ValueError:
            out.append(("raises", "ValueError"))
    return out

def failure_detail_text(task, test_inputs, expected_list, graded):
    lines = []
    for args, (kind, exp), pt in zip(test_inputs, expected_list, graded["per_test"]):
        if pt["pass"]:
            continue
        if kind == "value":
            lines.append(f"- Input {args!r}: expected {exp!r}, but {pt['reason']}")
        else:
            lines.append(f"- Input {args!r}: expected it to raise ValueError, but {pt['reason']}")
    return "\n".join(lines)

def run_one(task):
    tid = task["id"]
    func = task["func"]
    prompt = task["prompt"]
    test_inputs = task["test_inputs"]
    expected_list = expected_for(func, test_inputs)

    log(f"\n=== {tid} ===")
    log("  baseline attempt (shared across all 3 conditions)...")
    raw1 = ollama_client.generate(prompt)
    code1 = extract_code(raw1)
    g1 = grade(code1, func, test_inputs, expected_list)
    log(f"  baseline: {g1['n_pass']}/{g1['n_total']} ({g1['run_status']})")

    record = {
        "id": tid, "func": func, "prompt": prompt,
        "baseline": {"code": code1, "raw": raw1, "grade": g1},
    }

    if g1["n_pass"] == g1["n_total"]:
        record["no_retry"] = {"final": g1, "attempts_used": 1}
        record["blind_retry"] = {"attempts": [g1], "final": g1, "attempts_used": 1}
        record["error_aware_retry"] = {"attempts": [g1], "final": g1, "attempts_used": 1}
        log("  baseline already fully passes; no retries fired for any condition.")
        return record

    # NO RETRY condition: just the baseline.
    record["no_retry"] = {"final": g1, "attempts_used": 1}

    # BLIND RETRY: same exact prompt again, no feedback.
    blind_attempts = [{"code": code1, "raw": raw1, "grade": g1}]
    for i in range(MAX_EXTRA_ATTEMPTS):
        log(f"  blind retry attempt {i+2}...")
        raw = ollama_client.generate(prompt)
        code = extract_code(raw)
        g = grade(code, func, test_inputs, expected_list)
        log(f"  blind retry {i+2}: {g['n_pass']}/{g['n_total']} ({g['run_status']})")
        blind_attempts.append({"code": code, "raw": raw, "grade": g})
        if g["n_pass"] == g["n_total"]:
            break
    record["blind_retry"] = {
        "attempts": [a["grade"] for a in blind_attempts],
        "attempts_full": blind_attempts,
        "final": blind_attempts[-1]["grade"],
        "attempts_used": len(blind_attempts),
    }

    # ERROR-AWARE RETRY: feed back the actual failing-test detail.
    ea_attempts = [{"code": code1, "raw": raw1, "grade": g1}]
    cur_code, cur_grade = code1, g1
    for i in range(MAX_EXTRA_ATTEMPTS):
        detail = failure_detail_text(task, test_inputs, expected_list, cur_grade)
        followup = (
            f"Here is a Python function you wrote:\n\n```python\n{cur_code}\n```\n\n"
            f"It fails these test cases:\n{detail}\n\n"
            "Fix the function so it passes all of them. Return only the corrected "
            "function, no example usage, no explanation."
        )
        log(f"  error-aware retry attempt {i+2}...")
        raw = ollama_client.generate(followup)
        code = extract_code(raw)
        g = grade(code, func, test_inputs, expected_list)
        log(f"  error-aware retry {i+2}: {g['n_pass']}/{g['n_total']} ({g['run_status']})")
        ea_attempts.append({"code": code, "raw": raw, "grade": g})
        cur_code, cur_grade = code, g
        if g["n_pass"] == g["n_total"]:
            break
    record["error_aware_retry"] = {
        "attempts": [a["grade"] for a in ea_attempts],
        "attempts_full": ea_attempts,
        "final": ea_attempts[-1]["grade"],
        "attempts_used": len(ea_attempts),
    }
    return record

def main():
    open(LOG_PATH, "w").close()
    with open(RESULTS_PATH, "w") as out:
        for task in TASKS:
            t0 = time.time()
            rec = run_one(task)
            rec["elapsed_sec"] = round(time.time() - t0, 1)
            out.write(json.dumps(rec, default=str) + "\n")
            out.flush()
    log("\nDONE.")

if __name__ == "__main__":
    main()
