import json, random

random.seed(7)

def make_task(i):
    # two-step arithmetic word problem, deterministic ground truth
    a = random.randint(12, 95)
    b = random.randint(3, 40)
    c = random.randint(2, 25)
    op2 = random.choice(["given away", "lost", "sold"])
    start = a
    after_buy = start + b
    after_loss = after_buy - c
    answer = after_loss
    text = (f"A shop had {a} notebooks. It received a new shipment of {b} more notebooks. "
            f"Then {c} notebooks were {op2}. How many notebooks does the shop have now?")
    return {"id": f"task_{i:02d}", "prompt": text, "answer": answer}

tasks = [make_task(i) for i in range(20)]
with open("/tmp/llm-judge-bench/tasks.json", "w") as f:
    json.dump(tasks, f, indent=2)
print(len(tasks), "tasks written")
for t in tasks[:3]:
    print(t)
