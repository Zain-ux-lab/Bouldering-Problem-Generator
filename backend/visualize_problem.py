"""
visualize_problem.py — draws the wall AND highlights a generated
climbing path on top of it, so we can visually verify the generator
is actually producing a sane, climbable-looking sequence.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from generate_wall import build_wall
from generator.generator import generate_problem
from models.wall import HoldType

COLORS = {
    HoldType.JUG: "#2563eb",
    HoldType.CRIMP: "#dc2626",
    HoldType.SLOPER: "#16a34a",
    HoldType.FOOTHOLD: "#6b7280",
}

wall = build_wall(angle_deg=40)
path = generate_problem(wall, min_moves=6, max_moves=10)

if path is None:
    raise SystemExit("No valid problem generated -- try loosening constraints")

fig, ax = plt.subplots(figsize=(7, 8.5))

ax.add_patch(Rectangle((0, 0), wall.width_cm, wall.height_cm,
                        fill=False, edgecolor="black", linewidth=2))
ax.axvline(wall.centerline_x, color="#eee", linestyle="--", linewidth=1, zorder=0)

# All holds, faint, as context
for h in wall.holds:
    ax.scatter(h.x, h.y, s=h.size * 8, color=COLORS[h.hold_type],
               alpha=0.25, edgecolor="none", zorder=2)

# Draw the path as connected line segments -- this is the actual "route"
path_holds = [wall.get_hold(hid) for hid in path]
xs = [h.x for h in path_holds]
ys = [h.y for h in path_holds]
ax.plot(xs, ys, color="#f59e0b", linewidth=2.5, zorder=3, alpha=0.9)

# Highlight the path holds fully opaque, on top of everything
for i, h in enumerate(path_holds):
    ax.scatter(h.x, h.y, s=h.size * 14, color=COLORS[h.hold_type],
               edgecolor="black", linewidth=1.5, zorder=4)
    label = "START" if i == 0 else ("FINISH" if i == len(path_holds) - 1 else str(i))
    ax.annotate(label, (h.x, h.y), textcoords="offset points", xytext=(8, 8), fontsize=9, fontweight="bold")

ax.set_xlim(-10, wall.width_cm + 10)
ax.set_ylim(-10, wall.height_cm + 10)
ax.set_aspect("equal")
ax.set_title(f"Generated problem: {len(path)-1} moves\n(all holds shown faded for context)")
ax.set_xlabel("cm")
ax.set_ylabel("cm")

plt.tight_layout()
plt.savefig("problem_preview.png", dpi=150)
print(f"Saved problem_preview.png -- {len(path)-1} move problem")
