"""Run the repo-instructions experiment: 14 bug-fix tasks x 3 conditions (none / concise /
long-verbose instructions), one completion each, scored deterministically by running pytest
against the model's returned code. Logs every trial to raw_results.jsonl.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(__file__))

from tasks import TASKS  # noqa: E402
from llm_client import generate_text  # noqa: E402

HERE = os.path.dirname(__file__)

with open(os.path.join(HERE, "instructions_concise.md")) as f:
    CONCISE = f.read()
with open(os.path.join(HERE, "instructions_long.md")) as f:
    LONG = f.read()

CONDITIONS = {
    "none": None,
    "concise": CONCISE,
    "long": LONG,
}

CODE_FENCE_RE = re.compile(r"```(?:python)?\n(.*?)```", re.DOTALL)


def extract_code(raw):
    """Pull a Python function body out of a model response. Prefer a fenced code block; fall
    back to the raw text (minus any leading explanation lines) if no fence is present."""
    m = CODE_FENCE_RE.search(raw)
    if m:
        return m.group(1).strip()
    # No fence: assume the response is already just code, strip common prose prefixes
    lines = raw.strip().splitlines()
    code_start = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("def "):
            code_start = i
            break
    return "\n".join(lines[code_start:]).strip()


def run_pytest(code, test_code, timeout=20):
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "solution.py"), "w") as f:
            f.write(code)
        with open(os.path.join(d, "test_solution.py"), "w") as f:
            f.write(test_code)
        try:
            r = subprocess.run(
                [sys.executable, "-m", "pytest", "test_solution.py", "-q"],
                cwd=d, capture_output=True, text=True, timeout=timeout,
            )
            return r.returncode == 0, (r.stdout + r.stderr)[-1500:]
        except subprocess.TimeoutExpired:
            return False, "TIMEOUT running pytest"


def build_prompt(task, instructions):
    parts = []
    if instructions:
        parts.append(instructions)
        parts.append("\n---\n")
    parts.append(
        f"Task: {task['description']}\n\n"
        f"Here is the current (buggy) implementation:\n\n```python\n{task['buggy_code']}```\n\n"
        "Return ONLY the corrected function, as a single Python code block. No other text."
    )
    return "\n".join(parts)


def main():
    results = []
    out_path = os.path.join(HERE, "raw_results.jsonl")
    out_f = open(out_path, "w")
    provider_used = set()
    for cond_name, instructions in CONDITIONS.items():
        for task in TASKS:
            prompt = build_prompt(task, instructions)
            trial = {"task_id": task["id"], "condition": cond_name}
            try:
                raw, provider = generate_text(prompt, provider="auto")
                provider_used.add(provider)
                trial["provider"] = provider
                trial["raw_response"] = raw
                code = extract_code(raw)
                trial["extracted_code"] = code
                if not code.strip().startswith("def "):
                    trial["pass"] = False
                    trial["parse_error"] = True
                    trial["pytest_output"] = "extracted code did not start with 'def ' -- treated as parse failure"
                else:
                    passed, pytest_out = run_pytest(code, task["test_code"])
                    trial["pass"] = passed
                    trial["parse_error"] = False
                    trial["pytest_output"] = pytest_out
            except Exception as e:
                trial["pass"] = False
                trial["parse_error"] = True
                trial["error"] = str(e)
            results.append(trial)
            out_f.write(json.dumps(trial) + "\n")
            out_f.flush()
            print(f"{cond_name:8s} {task['id']:25s} -> {'PASS' if trial.get('pass') else 'FAIL'}", flush=True)
            time.sleep(1.0)  # be polite to the free-tier rate limit

    out_f.close()

    # Summary
    print("\n=== PASS RATES ===")
    for cond_name in CONDITIONS:
        subset = [r for r in results if r["condition"] == cond_name]
        n_pass = sum(1 for r in subset if r["pass"])
        print(f"{cond_name:8s}: {n_pass}/{len(subset)} ({100*n_pass/len(subset):.1f}%)")
    print("\nProviders used:", provider_used)


if __name__ == "__main__":
    main()
