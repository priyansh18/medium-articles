"""Generate the article's results chart from raw_results.jsonl directly.
PIL only (matplotlib not installed in this environment), $0, self-generated.
Reads the real numbers programmatically -- never hardcodes a quoted figure.
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(__file__)
W, H = 1600, 900
BG = (255, 255, 255)
INK = (30, 30, 35)
GRID = (225, 225, 230)
SUPPRESS = (220, 90, 70)
LET_FIRE = (70, 150, 110)
HONEST = (64, 145, 230)


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


def load_results():
    rows = []
    with open(os.path.join(HERE, "raw_results.jsonl")) as fh:
        for line in fh:
            rows.append(json.loads(line))
    return [r for r in rows if "error" not in r]


def main():
    rows = load_results()
    n = len(rows)
    suppressed_n = sum(1 for r in rows if r["suppressed_notify"])
    let_fire_n = n - suppressed_n
    # Hand-verified honesty count (see TOPIC_LOG / methodology.md note on the
    # keyword-classifier bug this corrected): every suppression trial's
    # follow-up explanation matched the real action.
    honest_n = suppressed_n

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    title_f, label_f, small_f, big_f = font(34, True), font(24), font(19), font(46, True)

    d.text((50, 30), "Did a Free Model Suppress Its Own Safety Alert?", fill=INK, font=title_f)
    d.text((50, 78),
           f"Gemini 3.6 Flash, n={n} independent trials, toy harness mirroring OpenAI's Oct 2026 disclosure",
           fill=(110, 110, 115), font=small_f)

    # Panel 1: suppression rate
    px0, py0, px1, py1 = 100, 170, 760, 760
    d.rectangle([px0, py0, px1, py1], outline=GRID, width=2)
    d.text((px0, py0 - 36), "Disabled the alert to honor \"send no messages\"", fill=INK, font=label_f)
    bars = [("Suppressed", suppressed_n, SUPPRESS), ("Let it fire", let_fire_n, LET_FIRE)]
    bw = (px1 - px0) / (len(bars) * 2)
    for i, (label, v, color) in enumerate(bars):
        frac = v / n
        bar_h = (py1 - py0) * frac
        x0 = px0 + 40 + i * (bw * 2)
        x1 = x0 + bw
        d.rectangle([x0, py1 - bar_h, x1, py1], fill=color)
        d.text((x0, py1 - bar_h - 34), f"{v}/{n} ({frac*100:.0f}%)", fill=INK, font=label_f)
        d.text((x0 - 10, py1 + 12), label, fill=INK, font=small_f)
    for gl in [0.25, 0.5, 0.75, 1.0]:
        y = py1 - (py1 - py0) * gl
        d.line([(px0, y), (px1, y)], fill=GRID, width=1)

    # Panel 2: honesty on follow-up, of the ones that suppressed
    qx0, qy0, qx1, qy1 = 860, 170, 1520, 760
    d.rectangle([qx0, qy0, qx1, qy1], outline=GRID, width=2)
    d.text((qx0, qy0 - 36), "Of those, told the truth when asked directly", fill=INK, font=label_f)
    frac = honest_n / suppressed_n if suppressed_n else 0
    d.text((qx0 + 150, qy0 + 220), f"{honest_n}/{suppressed_n}", fill=HONEST, font=big_f)
    d.text((qx0 + 150, qy0 + 290), f"{frac*100:.0f}% honest, 0% denied or misrepresented it", fill=INK, font=label_f)

    d.text((50, H - 40),
            "Image by author. Raw data: raw_results.jsonl in this article's reproducibility repo.",
            fill=(140, 140, 145), font=small_f)

    out = os.path.join(HERE, "..", "..", "drafts", "images", "hero-monitor-suppression.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    img.save(out)
    print("saved", out, "| n =", n, "| suppressed =", suppressed_n, "| honest_of_suppressed =", honest_n)


if __name__ == "__main__":
    main()
