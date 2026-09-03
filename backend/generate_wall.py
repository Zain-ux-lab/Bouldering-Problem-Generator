"""
generate_wall.py — builds one full Tension-Board-style wall.

IMPORTANT HONESTY NOTE: the exact hold positions on a real Tension Board
are proprietary (only available through their app). We don't have that
data. So this script generates a PLAUSIBLE, GRID-BASED layout inspired by
real dimensions/spacing conventions, clearly synthetic — not a copy of
the real board. This matches the honest-about-synthetic-data principle
from the very start of the project.

The core technique: we only ever design the LEFT half of the wall by
hand (well, programmatically), then MIRROR every hold across the
centerline to create its right-half twin automatically. This guarantees
perfect symmetry by construction, rather than us trying to manually
place holds symmetrically (error-prone).
"""

import random
from models.wall import Wall, Hold, HoldType, Side

random.seed(42)  # reproducible layout -- same "wall" every time we run this

# Real-world reference dimensions (standard Tension Board size)
WIDTH_CM = 244   # 8 ft
HEIGHT_CM = 305  # 10 ft


def generate_left_half_holds(width_cm, height_cm, grid_spacing_cm=11):
    """
    Places holds on a loose grid across the LEFT half of the wall only,
    with small random jitter so it doesn't look robotically perfect
    (real setter-placed holds never sit on an exact grid).
    """
    holds = []
    hold_id = 0
    half_width = width_cm / 2

    x = grid_spacing_cm / 2
    while x < half_width - 5:  # stay clear of the centerline
        y = grid_spacing_cm / 2
        while y < height_cm - 10:
            # Not every grid point gets a hold -- real boards have gaps
            if random.random() < 0.8:
                jitter_x = random.uniform(-5, 5)
                jitter_y = random.uniform(-5, 5)

                # Foot holds are smaller and more common lower on the wall;
                # slopers/crimps/jugs are the hand holds, roughly evenly spread
                if y < height_cm * 0.3 and random.random() < 0.4:
                    hold_type = HoldType.FOOTHOLD
                    size = random.uniform(3, 6)
                else:
                    hold_type = random.choice([HoldType.JUG, HoldType.CRIMP, HoldType.SLOPER])
                    size = {
                        HoldType.JUG: random.uniform(10, 16),
                        HoldType.CRIMP: random.uniform(3, 6),
                        HoldType.SLOPER: random.uniform(12, 20),
                    }[hold_type]

                holds.append(Hold(
                    id=hold_id,
                    x=round(x + jitter_x, 1),
                    y=round(y + jitter_y, 1),
                    hold_type=hold_type,
                    size=round(size, 1),
                    orientation=round(random.uniform(0, 360), 1),
                    side=Side.LEFT,
                ))
                hold_id += 1
            y += grid_spacing_cm
        x += grid_spacing_cm
    return holds


def mirror_holds(left_holds, width_cm, next_id_start):
    """
    Creates the RIGHT half of the wall by mirroring every left-half hold
    across the centerline: same y, same type/size/id-pairing, x is flipped.

    This is the key symmetry guarantee: right_x = width - left_x
    """
    mirrored = []
    next_id = next_id_start
    for h in left_holds:
        mirrored_x = width_cm - h.x
        twin = Hold(
            id=next_id,
            x=round(mirrored_x, 1),
            y=h.y,
            hold_type=h.hold_type,
            size=h.size,
            orientation=(360 - h.orientation) % 360,  # mirror the orientation too
            side=Side.RIGHT,
            mirror_id=h.id,
        )
        h.mirror_id = twin.id   # link both directions
        mirrored.append(twin)
        next_id += 1
    return mirrored


def build_wall(angle_deg=40) -> Wall:
    left_holds = generate_left_half_holds(WIDTH_CM, HEIGHT_CM)
    right_holds = mirror_holds(left_holds, WIDTH_CM, next_id_start=len(left_holds))
    all_holds = left_holds + right_holds
    return Wall(width_cm=WIDTH_CM, height_cm=HEIGHT_CM, angle_deg=angle_deg, holds=all_holds)


if __name__ == "__main__":
    wall = build_wall(angle_deg=40)
    print(f"Wall: {wall.width_cm}cm x {wall.height_cm}cm, angle {wall.angle_deg}°")
    print(f"Total holds: {len(wall.holds)}")
    print(f"  Left half:  {len(wall.holds_on(Side.LEFT))}")
    print(f"  Right half: {len(wall.holds_on(Side.RIGHT))}")

    from collections import Counter
    type_counts = Counter(h.hold_type.value for h in wall.holds)
    print("\nHold type breakdown:")
    for t, count in type_counts.items():
        print(f"  {t}: {count}")

    # Sanity check the symmetry: pick one hold, confirm its mirror really
    # is at the mirrored x position
    sample = wall.holds[3]
    mirror = wall.get_hold(sample.mirror_id)
    print(f"\nSymmetry check: hold {sample.id} at x={sample.x} <-> mirror {mirror.id} at x={mirror.x}")
    print(f"  width - {sample.x} = {round(wall.width_cm - sample.x, 1)}  (should equal mirror's x)")
