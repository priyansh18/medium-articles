"""Generate the two article images from summary.json / raw_results.jsonl.
PIL only (matplotlib not installed in this environment), $0, self-generated.
Reads the real numbers programmatically -- never hardcodes a quoted figure,
per the 10-12 lesson logged in TOPIC_LOG.md about diagram generators drifting
from the actual data.
"""
import json
from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 900
BG = (255, 255, 255)
INK = (30, 30, 35)
GRID = (225, 225, 230)
CHEAP = (64, 145, 230)
STRONG = (235, 94, 60)
ROUTED = (120, 80, 220)


def font(size, bold=False):
    paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def chart_1(summary):
    """Two-panel: overall accuracy, and total cost, per strategy."""
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    title_f, label_f, small_f = font(34, True), font(24), font(20)

    d.text((50, 30), "Cheap vs. Strong vs. Routed: Accuracy and Cost on 30 Tasks", fill=INK, font=title_f)
    d.text((50, 78), "Local Ollama benchmark, llama3.2:1b (cheap tier) vs llama3.1:8b (strong tier), temp=0, n=30", fill=(110, 110, 115), font=small_f)

    strategies = ["always_cheap", "always_strong", "routed"]
    labels = ["Always cheap", "Always strong", "Routed\n(confidence<70 escalates)"]
    colors = [CHEAP, STRONG, ROUTED]

    # Panel 1: accuracy (left half)
    px0, py0, px1, py1 = 100, 160, 760, 760
    d.rectangle([px0, py0, px1, py1], outline=GRID, width=2)
    d.text((px0, py0 - 36), "Overall accuracy", fill=INK, font=label_f)
    maxv = 1.0
    bw = (px1 - px0) / (len(strategies) * 2)
    for i, s in enumerate(strategies):
        v = summary["overall_accuracy"][s]
        bar_h = (py1 - py0) * (v / maxv)
        x0 = px0 + 40 + i * (bw * 2)
        x1 = x0 + bw
        d.rectangle([x0, py1 - bar_h, x1, py1], fill=colors[i])
        d.text((x0, py1 - bar_h - 30), f"{v*100:.1f}%", fill=INK, font=label_f)
        d.text((x0 - 10, py1 + 10), labels[i], fill=INK, font=small_f)
    for gl in [0.25, 0.5, 0.75, 1.0]:
        y = py1 - (py1 - py0) * gl
        d.line([(px0, y), (px1, y)], fill=GRID, width=1)
        d.text((px1 + 8, y - 8), f"{int(gl*100)}%", fill=(140, 140, 145), font=small_f)

    # Panel 2: cost (right half)
    qx0, qy0, qx1, qy1 = 880, 160, 1540, 760
    d.rectangle([qx0, qy0, qx1, qy1], outline=GRID, width=2)
    d.text((qx0, qy0 - 36), "Total cost, 30 tasks (illustrative, published hosted pricing)", fill=INK, font=label_f)
    maxc = max(summary["total_cost_usd"].values())
    bw2 = (qx1 - qx0) / (len(strategies) * 2)
    for i, s in enumerate(strategies):
        v = summary["total_cost_usd"][s]
        bar_h = (qy1 - qy0) * (v / maxc)
        x0 = qx0 + 40 + i * (bw2 * 2)
        x1 = x0 + bw2
        d.rectangle([x0, qy1 - bar_h, x1, qy1], fill=colors[i])
        label_y = max(qy1 - bar_h - 30, qy0 + 12)
        d.text((x0, label_y), f"${v:.4f}", fill=INK, font=label_f)
        d.text((x0 - 10, qy1 + 10), labels[i], fill=INK, font=small_f)

    d.text((50, 830), "Image by author. Pricing: DeepSeek V4.1 Flash ($0.30/$1.20 per M tokens) for cheap tier, GPT-5.6 Sol ($4/$20 per M tokens) for strong tier, applied to real local token counts.", fill=(140, 140, 145), font=small_f)
    img.save("hero-cost-accuracy.png")


def chart_2(rows):
    """Escalation outcome breakdown: 5 categories, grounded in the ACTUAL
    final routed_correct outcome for every bucket (not a hypothetical
    plain-prompt answer) -- see analysis.md for why that distinction matters:
    the non-escalated buckets use the real routed-prompt answer, which on 5
    of 16 tasks differed from the plain-prompt answer used in the always-cheap
    condition, because the added confidence-reporting instruction itself
    changed what the cheap model answered."""
    cats = {
        "Wasted\n(escalated, cheap plain\nanswer was already right)": 0,
        "Helped\n(escalated, cheap wrong,\nstrong fixed it)": 0,
        "Still wrong\n(escalated, cheap wrong,\nstrong also wrong)": 0,
        "Not escalated,\nended correct": 0,
        "Not escalated,\nended wrong": 0,
    }
    keys = list(cats.keys())
    for r in rows:
        esc, cheap_ok, routed_ok = r["routed_escalated"], r["cheap_correct"], r["routed_correct"]
        if esc and routed_ok and cheap_ok:
            cats[keys[0]] += 1
        elif esc and routed_ok and not cheap_ok:
            cats[keys[1]] += 1
        elif esc and not routed_ok:
            cats[keys[2]] += 1
        elif not esc and routed_ok:
            cats[keys[3]] += 1
        else:
            cats[keys[4]] += 1

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    title_f, label_f, small_f = font(34, True), font(24), font(19)
    d.text((50, 30), "What the Confidence-Based Router Actually Did, Task by Task (n=30)", fill=INK, font=title_f)
    d.text((50, 78), "Escalates when the cheap model self-reports confidence below 70", fill=(110, 110, 115), font=small_f)

    colors = [(235, 150, 60), (70, 170, 110), (200, 70, 70), (210, 60, 130), (130, 130, 230)]
    px0, py0, px1, py1 = 120, 170, 1500, 740
    maxv = max(cats.values())
    bw = (px1 - px0) / (len(cats) * 1.5)
    for i, (k, v) in enumerate(cats.items()):
        bar_h = (py1 - py0) * (v / maxv) if maxv else 0
        x0 = px0 + i * (bw * 1.5)
        x1 = x0 + bw
        d.rectangle([x0, py1 - bar_h, x1, py1], fill=colors[i])
        d.text((x0 + bw / 2 - 10, py1 - bar_h - 34), str(v), fill=INK, font=label_f)
        for j, line in enumerate(k.split("\n")):
            d.text((x0 - 5, py1 + 12 + j * 24), line, fill=INK, font=small_f)
    for gl in range(0, maxv + 1, 2):
        y = py1 - (py1 - py0) * (gl / maxv) if maxv else py1
        d.line([(px0, y), (px1, y)], fill=GRID, width=1)

    d.text((50, 830), "Image by author, from raw_results.jsonl (30 tasks, 2 Ollama models, temp=0, seed=7).", fill=(140, 140, 145), font=small_f)
    img.save("escalation-breakdown.png")


if __name__ == "__main__":
    summary = json.load(open("summary.json"))
    rows = [json.loads(l) for l in open("raw_results.jsonl")]
    chart_1(summary)
    chart_2(rows)
    print("saved hero-cost-accuracy.png and escalation-breakdown.png")
