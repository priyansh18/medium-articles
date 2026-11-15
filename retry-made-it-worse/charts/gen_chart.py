"""Bar chart of the 3 tasks that actually produced retry data: baseline vs
final blind-retry score vs final error-aware-retry score. PIL only (no
matplotlib in this environment), same approach as llm-judge-rubber-stamp's
chart script."""
from PIL import Image, ImageDraw, ImageFont

TASKS = [
    ("next_greater_permutation", 2, 5, 2, 5, 2, 5),
    ("valid_parenthesis_with_star", 4, 6, 4, 6, 5, 6),
    ("decode_ways", 0, 6, 2, 6, 2, 6),
]
LABELS = ["next_greater_\npermutation", "valid_parenthesis_\nwith_star", "decode_ways"]

W, H = 900, 520
MARGIN_L, MARGIN_B, MARGIN_T = 70, 90, 60
plot_w = W - MARGIN_L - 40
plot_h = H - MARGIN_B - MARGIN_T

img = Image.new("RGB", (W, H), "white")
draw = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 13)
    font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
except Exception:
    font = font_small = font_title = ImageFont.load_default()

draw.text((MARGIN_L, 18), "Baseline vs. retry, final score (of total tests)", fill="black", font=font_title)

colors = {"baseline": (120, 120, 120), "blind": (66, 135, 245), "error_aware": (219, 68, 55)}

n_groups = len(TASKS)
group_w = plot_w / n_groups
bar_w = group_w / 4.2

draw.line([(MARGIN_L, MARGIN_T), (MARGIN_L, MARGIN_T + plot_h)], fill="black", width=2)
draw.line([(MARGIN_L, MARGIN_T + plot_h), (MARGIN_L + plot_w, MARGIN_T + plot_h)], fill="black", width=2)

for gy in range(0, 7):
    y = MARGIN_T + plot_h - (gy / 6) * plot_h
    draw.line([(MARGIN_L, y), (MARGIN_L + plot_w, y)], fill=(230, 230, 230), width=1)
    draw.text((MARGIN_L - 25, y - 7), str(gy), fill="black", font=font_small)

for idx, (name, b_pass, b_tot, bl_pass, bl_tot, ea_pass, ea_tot) in enumerate(TASKS):
    gx = MARGIN_L + idx * group_w + group_w * 0.15
    for j, (val, tot, color) in enumerate([
        (b_pass, b_tot, colors["baseline"]),
        (bl_pass, bl_tot, colors["blind"]),
        (ea_pass, ea_tot, colors["error_aware"]),
    ]):
        bx = gx + j * (bar_w + 8)
        bar_h = (val / tot) * plot_h
        by = MARGIN_T + plot_h - bar_h
        draw.rectangle([bx, by, bx + bar_w, MARGIN_T + plot_h], fill=color)
        draw.text((bx + 2, by - 18), f"{val}/{tot}", fill="black", font=font_small)
    label_x = MARGIN_L + idx * group_w + group_w / 2
    for li, line in enumerate(LABELS[idx].split("\n")):
        draw.text((label_x - 60, MARGIN_T + plot_h + 10 + li * 16), line, fill="black", font=font_small, anchor=None)

legend_y = H - 28
swatches = [("baseline", colors["baseline"]), ("blind retry (final)", colors["blind"]), ("error-aware retry (final)", colors["error_aware"])]
lx = MARGIN_L
for label, color in swatches:
    draw.rectangle([lx, legend_y, lx + 14, legend_y + 14], fill=color)
    draw.text((lx + 20, legend_y - 1), label, fill="black", font=font_small)
    lx += 20 + len(label) * 7 + 30

img.save("results-chart.png")
print("saved results-chart.png")
