import json, re, time, urllib.request

OLLAMA = "http://localhost:11434/api/generate"
WEAK = "llama3.2:1b"
STRONG = "llama3.1:8b"
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

def extract_number(text):
    nums = re.findall(r"-?\d+", text.replace(",", ""))
    return int(nums[-1]) if nums else None

def solve_prompt(p):
    return f"{p}\n\nShow your steps briefly, then give your final numeric answer on the last line as exactly: FINAL ANSWER: <number>"

def judge_prompt(task_prompt, candidate_text):
    return ("You are grading a student's solution to a word problem. Decide only whether the "
            "student's FINAL numeric answer is correct or incorrect for the problem below. "
            "Reply with exactly one word on the first line: CORRECT or INCORRECT.\n\n"
            f"PROBLEM:\n{task_prompt}\n\nSTUDENT SOLUTION:\n{candidate_text}\n\nVerdict (CORRECT or INCORRECT):")

def judge_verdict(task_prompt, candidate_text):
    raw, dt = ollama_generate(JUDGE, judge_prompt(task_prompt, candidate_text))
    first = raw.strip().splitlines()[0].upper() if raw.strip() else ""
    v = "CORRECT" if "CORRECT" in first and "INCORRECT" not in first else ("INCORRECT" if "INCORRECT" in first else "UNPARSEABLE")
    return v, raw, dt

with open("/tmp/llm-judge-bench/tasks_hard.json") as f:
    tasks = json.load(f)

rows = []
for t in tasks:
    row = {"id": t["id"], "prompt": t["prompt"], "ground_truth": t["answer"]}
    for label, model in (("weak_llama3.2_1b", WEAK), ("strong_llama3.1_8b", STRONG)):
        raw, dt = ollama_generate(model, solve_prompt(t["prompt"]))
        extracted = extract_number(raw)
        actually_correct = extracted == t["answer"]
        verdict, judge_raw, judge_dt = judge_verdict(t["prompt"], raw)
        row[label] = {"raw_answer": raw, "extracted_number": extracted, "actually_correct": actually_correct,
                      "judge_verdict": verdict, "judge_raw": judge_raw, "gen_seconds": round(dt,2), "judge_seconds": round(judge_dt,2)}
        print(f"{t['id']} [{label}] extracted={extracted} truth={t['answer']} actually_correct={actually_correct} judge={verdict}")
    rows.append(row)

with open("/tmp/llm-judge-bench/raw_results_parta_hard.jsonl", "w") as f:
    for row in rows:
        f.write(json.dumps({"part": "part_a_hard", **row}) + "\n")
print("done")
