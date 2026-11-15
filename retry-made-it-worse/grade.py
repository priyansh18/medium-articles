"""Grading helpers: run model-generated code against the reference's expected
outputs for the same inputs, in an isolated subprocess (never imported into
the orchestrator's own process)."""
import json
import re
import subprocess
import sys
import tempfile
import os

HARNESS_TEMPLATE = '''
import sys, json
sys.path.insert(0, {sandbox_dir!r})
import candidate

FUNC_NAME = {func_name!r}
TEST_INPUTS = {test_inputs!r}

results = []
fn = getattr(candidate, FUNC_NAME, None)
if fn is None:
    print(json.dumps({{"error": "function_not_found"}}))
    sys.exit(0)

for args in TEST_INPUTS:
    entry = {{}}
    try:
        val = fn(*args)
        entry["ok"] = True
        entry["value"] = val
    except Exception as e:
        entry["ok"] = False
        entry["exception_type"] = type(e).__name__
        entry["exception_msg"] = str(e)
    results.append(entry)

print(json.dumps({{"results": results}}, default=str))
'''

def extract_code(raw_text):
    """Pull the first python code block out of a model response; fall back
    to the raw text if no fenced block is present."""
    m = re.search(r"```(?:python)?\s*\n(.*?)```", raw_text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return raw_text.strip()

def _normalize(v):
    if isinstance(v, (list, tuple)):
        return tuple(_normalize(x) for x in v)
    if isinstance(v, float):
        return round(v, 4)
    return v

def run_candidate(code_text, func_name, test_inputs, timeout=15):
    """Writes the candidate code to an isolated temp dir and runs a harness
    subprocess (python3 -I, no repo access) against each test input.
    Returns a dict: {status, per_test: [...]}."""
    with tempfile.TemporaryDirectory(prefix="job20_retry_sandbox_") as d:
        cand_path = os.path.join(d, "candidate.py")
        with open(cand_path, "w") as f:
            f.write(code_text)
        harness_path = os.path.join(d, "harness.py")
        with open(harness_path, "w") as f:
            f.write(HARNESS_TEMPLATE.format(
                sandbox_dir=d, func_name=func_name, test_inputs=test_inputs
            ))
        try:
            proc = subprocess.run(
                [sys.executable, "-I", harness_path],
                capture_output=True, text=True, timeout=timeout, cwd=d,
            )
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "per_test": []}
        if proc.returncode != 0:
            return {"status": "crash", "stderr": proc.stderr[-2000:], "per_test": []}
        try:
            out = json.loads(proc.stdout.strip().splitlines()[-1])
        except Exception:
            return {"status": "unparsable_output", "stdout": proc.stdout[-1000:],
                     "stderr": proc.stderr[-1000:], "per_test": []}
        if "error" in out:
            return {"status": out["error"], "per_test": []}
        return {"status": "ran", "per_test": out["results"]}

def grade(code_text, func_name, test_inputs, expected_list):
    """expected_list[i] is either ("value", v) or ("raises", ExceptionClassName)."""
    run = run_candidate(code_text, func_name, test_inputs)
    per_test_graded = []
    n_pass = 0
    if run["status"] != "ran":
        for kind, exp in expected_list:
            per_test_graded.append({"pass": False, "reason": run["status"]})
        return {"n_pass": 0, "n_total": len(expected_list), "run_status": run["status"],
                "per_test": per_test_graded}
    for entry, (kind, exp) in zip(run["per_test"], expected_list):
        ok = False
        reason = ""
        if kind == "value":
            if entry.get("ok"):
                if _normalize(entry["value"]) == _normalize(exp):
                    ok = True
                else:
                    reason = f"got {entry['value']!r} expected {exp!r}"
            else:
                reason = f"raised {entry.get('exception_type')}: {entry.get('exception_msg')}"
        elif kind == "raises":
            if not entry.get("ok") and entry.get("exception_type") == exp:
                ok = True
            elif entry.get("ok"):
                reason = f"did not raise, returned {entry.get('value')!r}"
            else:
                reason = f"raised {entry.get('exception_type')} not {exp}"
        if ok:
            n_pass += 1
        per_test_graded.append({"pass": ok, "reason": reason})
    return {"n_pass": n_pass, "n_total": len(expected_list), "run_status": "ran",
            "per_test": per_test_graded}
