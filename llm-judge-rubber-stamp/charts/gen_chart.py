"""Hero/results chart: plain judge vs chain-of-thought judge catch rate on 41 deliberately
wrong answers. Built with PIL (matplotlib unavailable in this environment). $0, no license risk.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 900
BG = (255, 255, 255)
INK = (30, 30, 35)
BLUE = (59, 130, 246)
ORANGE = (249, 115, 22)
GRID = (230, 230, 232)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)


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


title_f = font(34, bold=True)
sub_f = font(20)
label_f = font(24, bold=True)
num_f = font(40, bold=True)
small_f = font(18)

title = "Catching Wrong Answers: Plain Judge vs. Chain-of-Thought Judge"
d.text((60, 40), title, font=title_f, fill=INK)
sub = "41 deliberately wrong answers graded by the same local model (llama3.1:8b), two prompts only"
d.text((60, 90), sub, font=sub_f, fill=(90, 90, 95))

# chart area
chart_top = 180
chart_bottom = 740
chart_left = 220
chart_right = 1400
max_val = 100

# gridlines
for pct in (0, 25, 50, 75, 100):
    y = chart_bottom - (pct / 100) * (chart_bottom - chart_top)
    d.line([(chart_left, y), (chart_right, y)], fill=GRID, width=2)
    d.text((chart_left - 70, y - 10), f"{pct}%", font=small_f, fill=(120, 120, 125))

bars = [
    ("Plain judge\n(\"CORRECT or\nINCORRECT?\")", 1 / 41 * 100, BLUE, "1 / 41 caught\n(~2.4%)"),
    ("Chain-of-thought judge\n(solve it first,\nthen compare)", 41 / 41 * 100, ORANGE, "41 / 41 caught\n(100%)"),
]

bar_width = 320
gap = 240
start_x = chart_left + 150
for i, (label, pct, color, annotation) in enumerate(bars):
    x0 = start_x + i * (bar_width + gap)
    x1 = x0 + bar_width
    y1 = chart_bottom
    y0 = chart_bottom - (pct / 100) * (chart_bottom - chart_top)
    d.rectangle([x0, y0, x1, y1], fill=color)
    # value label above bar
    val_text = f"{pct:.1f}%" if pct not in (100.0,) else "100%"
    if abs(pct - (1 / 41 * 100)) < 0.01:
        val_text = "2.4%"
    bbox = d.textbbox((0, 0), val_text, font=num_f)
    tw = bbox[2] - bbox[0]
    d.text((x0 + (bar_width - tw) / 2, y0 - 55), val_text, font=num_f, fill=INK)
    # category label below axis
    lines = label.split("\n")
    ly = chart_bottom + 20
    for line in lines:
        bbox = d.textbbox((0, 0), line, font=label_f)
        tw = bbox[2] - bbox[0]
        d.text((x0 + (bar_width - tw) / 2, ly), line, font=label_f, fill=INK)
        ly += 30

# axis line
d.line([(chart_left, chart_bottom), (chart_right, chart_bottom)], fill=INK, width=3)
d.line([(chart_left, chart_top), (chart_left, chart_bottom)], fill=INK, width=3)

d.text((60, 850), "Wrong-answer catch rate, same model, same 41 answers, one prompt change", font=small_f, fill=(120, 120, 125))

img.save("/tmp/llm-judge-bench/results-chart.png")
print("saved /tmp/llm-judge-bench/results-chart.png")
