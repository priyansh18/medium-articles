"""Build a bar chart of pass rate per instruction condition from raw_results.jsonl. PIL only, no
matplotlib dependency, no AI image generator."""
import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(__file__)
CONDITIONS = ["none", "concise", "long"]
LABELS = {"none": "No instructions", "concise": "Concise (~10 lines)", "long": "Long verbose (~150 lines)"}


def load_pass_rates():
    counts = {c: [0, 0] for c in CONDITIONS}  # [n_pass, n_total]
    with open(os.path.join(HERE, "raw_results.jsonl")) as f:
        for line in f:
            r = json.loads(line)
            counts[r["condition"]][1] += 1
            if r.get("pass"):
                counts[r["condition"]][0] += 1
    return {c: (p / t * 100 if t else 0.0, p, t) for c, (p, t) in counts.items()}


def main():
    rates = load_pass_rates()
    W, H = 900, 560
    margin_l, margin_b, margin_t = 90, 100, 70
    chart_h = H - margin_b - margin_t
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 26)
        font_label = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        font_val = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
    except Exception:
        font_title = font_label = font_val = ImageFont.load_default()

    d.text((margin_l, 20), "Pass rate by instruction condition (14 bug-fix tasks, n=14 per bar)", fill="black", font=font_title)

    # axes
    d.line([(margin_l, margin_t), (margin_l, margin_t + chart_h)], fill="black", width=2)
    d.line([(margin_l, margin_t + chart_h), (W - 40, margin_t + chart_h)], fill="black", width=2)
    for pct in (0, 25, 50, 75, 100):
        y = margin_t + chart_h - (pct / 100) * chart_h
        d.line([(margin_l - 5, y), (W - 40, y)], fill="#dddddd", width=1)
        d.text((10, y - 8), f"{pct}%", fill="black", font=font_label)

    bar_w = 160
    gap = 90
    colors = {"none": "#9e9e9e", "concise": "#4caf50", "long": "#e07b39"}
    x = margin_l + 60
    for c in CONDITIONS:
        pct, p, t = rates[c]
        bar_h = (pct / 100) * chart_h
        y0 = margin_t + chart_h - bar_h
        d.rectangle([x, y0, x + bar_w, margin_t + chart_h], fill=colors[c])
        d.text((x + bar_w / 2 - 20, y0 - 28), f"{p}/{t}", fill="black", font=font_val)
        d.text((x - 10, margin_t + chart_h + 12), LABELS[c], fill="black", font=font_label)
        x += bar_w + gap

    out_path = os.path.join(os.path.dirname(HERE), "..", "images", "pass-rate-by-condition.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    print("Saved chart to", os.path.abspath(out_path))


if __name__ == "__main__":
    main()
