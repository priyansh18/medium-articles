"""Sanity check: confirm every task's buggy_code genuinely fails its own test_code."""
import subprocess
import sys
import tempfile
import os

sys.path.insert(0, os.path.dirname(__file__))
from tasks import TASKS


def run_pytest(code, test_code):
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "solution.py"), "w") as f:
            f.write(code)
        with open(os.path.join(d, "test_solution.py"), "w") as f:
            f.write(test_code)
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "test_solution.py", "-q"],
            cwd=d, capture_output=True, text=True, timeout=20,
        )
        return r.returncode == 0, r.stdout + r.stderr


if __name__ == "__main__":
    all_bugs_real = True
    for t in TASKS:
        passed, out = run_pytest(t["buggy_code"], t["test_code"])
        status = "BUG NOT DETECTED (test passed on buggy code!)" if passed else "ok (test fails on buggy code)"
        if passed:
            all_bugs_real = False
        print(f"{t['id']}: {status}")
    print()
    print("ALL BUGS REAL:" , all_bugs_real)
