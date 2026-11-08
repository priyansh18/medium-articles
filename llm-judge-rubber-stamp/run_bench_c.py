import json, time, urllib.request

OLLAMA = "http://localhost:11434/api/generate"
JUDGE = "llama3.1:8b"

def ollama_generate(model, prompt, temperature=0.0, seed=7):
    payload = {"model": model, "prompt": prompt, "stream": False,
               "options": {"temperature": temperature, "seed": seed}}
    req = urllib.request.Request(OLLAMA, data=json.dumps(payload).encode(),
                                  headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read())
    return body.get("response", "").strip(), time.time() - t0

def cot_judge_prompt(task_prompt, candidate_text):
    return (
        "You are grading a student's solution to a word problem.\n"
        "Step 1: Solve the problem yourself from scratch, showing your own work, and state your "
        "own final numeric answer as: MY ANSWER: <number>\n"
        "Step 2: Compare your own answer to the student's final answer below. If they match, say "
        "CORRECT. If they do not match, say INCORRECT.\n"
        "End your reply with the verdict on its own last line as exactly: VERDICT: CORRECT or VERDICT: INCORRECT\n\n"
        f"PROBLEM:\n{task_prompt}\n\nSTUDENT SOLUTION:\n{candidate_text}\n"
    )

def parse_verdict(raw):
    for line in reversed(raw.strip().splitlines()):
        u = line.upper()
        if "VERDICT" in u:
            if "INCORRECT" in u:
                return "INCORRECT"
            if "CORRECT" in u:
                return "CORRECT"
    u = raw.upper()
    if "INCORRECT" in u:
        return "INCORRECT"
    if "CORRECT" in u:
        return "CORRECT"
    return "UNPARSEABLE"

rows_a = [json.loads(l) for l in open("/tmp/llm-judge-bench/raw_results_parta_hard.jsonl")]

results = []
for row in rows_a:
    for label in ("weak_llama3.2_1b", "strong_llama3.1_8b"):
        cand = row[label]
        raw, dt = ollama_generate(JUDGE, cot_judge_prompt(row["prompt"], cand["raw_answer"]))
        verdict = parse_verdict(raw)
        correct_judge_call = (verdict == "CORRECT") == cand["actually_correct"]
        results.append({
            "id": row["id"], "label": label, "ground_truth": row["ground_truth"],
            "actually_correct": cand["actually_correct"], "cot_judge_verdict": verdict,
            "cot_judge_raw": raw, "correct_judge_call": correct_judge_call, "seconds": round(dt, 2),
        })
        print(f"{row['id']} [{label}] actually_correct={cand['actually_correct']} cot_judge={verdict} judge_call_correct={correct_judge_call}")

with open("/tmp/llm-judge-bench/raw_results_cot_judge.jsonl", "w") as f:
    for r in results:
        f.write(json.dumps(r) + "\n")

n = len(results)
agree = sum(r["correct_judge_call"] for r in results)
print(f"\nCoT judge agreement with ground truth: {agree}/{n} = {agree/n:.1%}")
