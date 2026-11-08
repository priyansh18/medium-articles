#!/usr/bin/env python3
"""LLM-as-judge self-preference + verbosity bias benchmark. $0, local Ollama only.

Part A (self-preference): llama3.2:1b (weak) and llama3.1:8b (strong) each solve the same
20 deterministic arithmetic word problems. llama3.1:8b then acts as a BLIND judge (sees only
the task + a candidate answer, never which model produced it, never the ground truth) and
grades each candidate correct/incorrect. We then compare judge accuracy on its OWN answers
vs the other model's answers, holding true correctness constant, to see if the judge is more
lenient toward text that reads like its own output.

Part B (verbosity bias): for a subset of tasks, we hand-construct a WRONG final numeric
answer (so ground truth = incorrect for every variant) and present it in three fixed
verbosity levels (terse / medium / verbose-with-hedging) with the wrong number held constant.
The same blind judge grades each variant. If the judge's correct/incorrect verdict shifts
toward "correct" as verbosity increases despite the wrong number never changing, that is
verbosity bias in this judge, not accuracy improving.
"""
import json
import re
import time
import urllib.request

OLLAMA = "http://localhost:11434/api/generate"
WEAK = "llama3.2:1b"
STRONG = "llama3.1:8b"
JUDGE = "llama3.1:8b"


def ollama_generate(model, prompt, temperature=0.0, seed=7):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "seed": seed},
    }
    req = urllib.request.Request(
        OLLAMA, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read())
    dt = time.time() - t0
    return body.get("response", "").strip(), dt


def extract_number(text):
    # last integer in the text is taken as the model's final answer
    nums = re.findall(r"-?\d+", text.replace(",", ""))
    return int(nums[-1]) if nums else None


def solve_prompt(task_prompt):
    return (
        f"{task_prompt}\n\n"
        "Think briefly, then give your final numeric answer on the last line as exactly: "
        "FINAL ANSWER: <number>"
    )


def judge_prompt(task_prompt, candidate_answer_text):
    return (
        "You are grading a student's solution to a word problem. Decide only whether the "
        "student's FINAL numeric answer is correct or incorrect for the problem below. "
        "Reply with exactly one word on the first line: CORRECT or INCORRECT.\n\n"
        f"PROBLEM:\n{task_prompt}\n\n"
        f"STUDENT SOLUTION:\n{candidate_answer_text}\n\n"
        "Verdict (CORRECT or INCORRECT):"
    )


def judge_verdict(task_prompt, candidate_text):
    raw, dt = ollama_generate(JUDGE, judge_prompt(task_prompt, candidate_text))
    first_line = raw.strip().splitlines()[0].upper() if raw.strip() else ""
    verdict = "CORRECT" if "CORRECT" in first_line and "INCORRECT" not in first_line else (
        "INCORRECT" if "INCORRECT" in first_line else "UNPARSEABLE"
    )
    return verdict, raw, dt


def main():
    with open("/tmp/llm-judge-bench/tasks.json") as f:
        tasks = json.load(f)

    results = {"part_a": [], "part_b": []}

    print("=== PART A: self-preference bias ===")
    for t in tasks:
        row = {"id": t["id"], "prompt": t["prompt"], "ground_truth": t["answer"]}
        for label, model in (("weak_llama3.2_1b", WEAK), ("strong_llama3.1_8b", STRONG)):
            raw, dt = ollama_generate(model, solve_prompt(t["prompt"]))
            extracted = extract_number(raw)
            actually_correct = extracted == t["answer"]
            verdict, judge_raw, judge_dt = judge_verdict(t["prompt"], raw)
            row[label] = {
                "raw_answer": raw,
                "extracted_number": extracted,
                "actually_correct": actually_correct,
                "judge_verdict": verdict,
                "judge_raw": judge_raw,
                "gen_seconds": round(dt, 2),
                "judge_seconds": round(judge_dt, 2),
            }
            print(
                f"{t['id']} [{label}] extracted={extracted} truth={t['answer']} "
                f"actually_correct={actually_correct} judge={verdict}"
            )
        results["part_a"].append(row)

    print("\n=== PART B: verbosity bias (wrong answer held constant) ===")
    verbosity_tasks = tasks[:10]
    for t in verbosity_tasks:
        wrong_answer = t["answer"] + 7  # deliberately wrong, fixed offset
        variants = {
            "terse": f"FINAL ANSWER: {wrong_answer}",
            "medium": (
                f"Adding the shipment and subtracting the amount removed gives the total. "
                f"FINAL ANSWER: {wrong_answer}"
            ),
            "verbose": (
                "Let me work through this carefully, step by step, to be sure. First I note "
                "the starting quantity mentioned in the problem. Next I account for the new "
                "shipment that arrives, which increases the total. After that I carefully "
                "subtract the quantity that was removed afterward, since that reduces the "
                "running total back down. Cross-checking this arithmetic once more for safety, "
                "I am confident in the following result. "
                f"FINAL ANSWER: {wrong_answer}"
            ),
        }
        row = {"id": t["id"], "prompt": t["prompt"], "ground_truth": t["answer"], "wrong_answer_used": wrong_answer}
        for level, text in variants.items():
            verdict, judge_raw, judge_dt = judge_verdict(t["prompt"], text)
            row[level] = {"text": text, "judge_verdict": verdict, "judge_raw": judge_raw, "judge_seconds": round(judge_dt, 2)}
            print(f"{t['id']} [{level}] wrong_answer={wrong_answer} judge={verdict}")
        results["part_b"].append(row)

    with open("/tmp/llm-judge-bench/raw_results.jsonl", "w") as f:
        for part in ("part_a", "part_b"):
            for row in results[part]:
                f.write(json.dumps({"part": part, **row}) + "\n")

    print("\nWrote /tmp/llm-judge-bench/raw_results.jsonl")


if __name__ == "__main__":
    main()
