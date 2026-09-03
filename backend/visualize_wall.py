"""
visualize_wall.py — draws the generated wall so we can SEE the symmetry
and hold layout, not just trust numbers.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from generate_wall import build_wall
from models.wall import HoldType, Side

COLORS = {
    HoldType.JUG: "#2563eb",       # blue
    HoldType.CRIMP: "#dc2626",      # red
    HoldType.SLOPER: "#16a34a",     # green
    HoldType.FOOTHOLD: "#6b7280",   # grey
}

wall = build_wall(angle_deg=40)

fig, ax = plt.subplots(figsize=(7, 8.5))

# Draw the wall boundary
ax.add_patch(Rectangle((0, 0), wall.width_cm, wall.height_cm,
                        fill=False, edgecolor="black", linewidth=2))

# Draw the centerline to make the symmetry visually obvious
ax.axvline(wall.centerline_x, color="#999", linestyle="--", linewidth=1)

# Draw every hold, sized and colored by type
for h in wall.holds:
    ax.scatter(h.x, h.y, s=h.size * 10, color=COLORS[h.hold_type],
               alpha=0.8, edgecolor="white", linewidth=0.5, zorder=3)

# Legend
for hold_type, color in COLORS.items():
    ax.scatter([], [], color=color, label=hold_type.value, s=80)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.03), ncol=4)

ax.set_xlim(-10, wall.width_cm + 10)
ax.set_ylim(-10, wall.height_cm + 10)
ax.set_aspect("equal")
ax.set_title(f"Generated Tension-Board-style wall\n{wall.width_cm}cm x {wall.height_cm}cm, {wall.angle_deg}° — {len(wall.holds)} holds (symmetric)")
ax.set_xlabel("cm")
ax.set_ylabel("cm")

plt.tight_layout()
plt.savefig("wall_preview.png", dpi=150)
print("Saved wall_preview.png")
