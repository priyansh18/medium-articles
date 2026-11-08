import json, random
import math

random.seed(11)

def make_task(i):
    trays = random.randint(6, 14)
    per_tray = random.randint(8, 20)
    sold_trays = random.randint(2, trays - 2)
    pct = random.choice([10, 15, 20, 25, 30])
    total = trays * per_tray
    remaining_after_sale = total - sold_trays * per_tray
    used_for_sample = math.floor(remaining_after_sale * pct / 100)
    answer = remaining_after_sale - used_for_sample
    text = (
        f"A bakery had {trays} trays of cookies with {per_tray} cookies on each tray. "
        f"It sold {sold_trays} full trays. Then it used {pct}% of the remaining cookies "
        f"(rounded down to the nearest whole cookie) for a sample display. "
        f"How many cookies are left after the sample display?"
    )
    return {
        "id": f"htask_{i:02d}",
        "prompt": text,
        "answer": answer,
        "work": {
            "total": total,
            "remaining_after_sale": remaining_after_sale,
            "used_for_sample": used_for_sample,
        },
    }

tasks = [make_task(i) for i in range(20)]
with open("/tmp/llm-judge-bench/tasks_hard.json", "w") as f:
    json.dump(tasks, f, indent=2)
for t in tasks[:4]:
    print(t)
print(len(tasks), "hard tasks written")
