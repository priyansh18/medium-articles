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

rows_b = [json.loads(l) for l in open("/tmp/llm-judge-bench/raw_results.jsonl") if json.loads(l)["part"] == "part_b"]

results = []
for row in rows_b:
    for level in ("terse", "medium", "verbose"):
        text = row[level]["text"]
        raw, dt = ollama_generate(JUDGE, cot_judge_prompt(row["prompt"], text))
        verdict = parse_verdict(raw)
        results.append({"id": row["id"], "level": level, "wrong_answer_used": row["wrong_answer_used"],
                         "cot_judge_verdict": verdict, "cot_judge_raw": raw, "seconds": round(dt, 2)})
        print(f"{row['id']} [{level}] wrong_answer={row['wrong_answer_used']} cot_judge={verdict}")

with open("/tmp/llm-judge-bench/raw_results_cot_judge_partb.jsonl", "w") as f:
    for r in results:
        f.write(json.dumps(r) + "\n")

n = len(results)
caught = sum(r["cot_judge_verdict"] == "INCORRECT" for r in results)
print(f"\nCoT judge caught {caught}/{n} of the held-constant wrong answers")
