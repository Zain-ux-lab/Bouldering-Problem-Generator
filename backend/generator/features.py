"""
features.py — turns a climbing problem (a path of hold ids) into a
numerical feature vector: the bridge between the generator and the ML model.

An ML model can't understand "a sequence of holds" directly -- it needs
numbers. This file's whole job is: given a path, calculate the numbers
that describe how hard it probably is.
"""

import math
from collections import Counter
from generator.constraints import distance
from generator.generator import suggest_footholds
from models.wall import HoldType


HOLD_DIFFICULTY = {
    # Rough, transparent difficulty weighting per hold type (0-1 scale).
    # This is OUR modeling choice, not a scientific fact -- worth being
    # able to explain/defend in an interview.
    HoldType.JUG: 0.1,       # easiest
    HoldType.SLOPER: 0.6,
    HoldType.FOOTHOLD: 0.3,
    HoldType.CRIMP: 0.9,     # hardest
}


def extract_features(wall, path):
    """
    path: list of hand-hold ids (as returned by generate_problem);
    path[0:2] is the two-hand start position, path[2:] are real moves.
    Returns a dict of named features -- deliberately a dict, not a bare
    list, so it stays self-documenting as the project grows.
    """
    holds = [wall.get_hold(hid) for hid in path]
    # holds[0] and holds[1] are the two-hand START position, not a real
    # climbing move -- exclude that span from move-distance statistics,
    # same way a climber's starting hand span isn't counted as "a move".
    real_moves = list(zip(holds[1:], holds[2:]))

    move_distances = [distance(a, b) for a, b in real_moves]

    # Direction changes: count how often the LEFT/RIGHT movement direction
    # flips (a rough proxy for how twisty/technical the problem feels)
    direction_changes = 0
    prev_dx_sign = None
    for a, b in real_moves:
        dx = b.x - a.x
        sign = 1 if dx > 0 else (-1 if dx < 0 else 0)
        if prev_dx_sign is not None and sign != 0 and sign != prev_dx_sign:
            direction_changes += 1
        if sign != 0:
            prev_dx_sign = sign

    hold_sizes = [h.size for h in holds]
    hold_type_counts = Counter(h.hold_type for h in holds)
    avg_hold_difficulty = sum(HOLD_DIFFICULTY[h.hold_type] for h in holds) / len(holds)

    # Every hold in `holds` is now guaranteed to be a hand hold (footholds
    # are excluded from the path entirely -- see generator.py v2), so this
    # is just the hand-hold size average directly.
    hand_hold_sizes = hold_sizes

    # foothold_ratio is redefined from v1: since footholds are no longer
    # PART of the path, this now measures something more useful -- what
    # fraction of hand moves actually have a nearby foothold available
    # (more available footholds = generally easier climbing).
    foot_suggestions = suggest_footholds(wall, path)
    foothold_ratio = sum(1 for f in foot_suggestions if f is not None) / len(foot_suggestions)

    return {
        "wall_angle": wall.angle_deg,
        "num_moves": len(real_moves),
        "vertical_gain": round(holds[-1].y - holds[0].y, 1),
        "horizontal_movement": round(sum(abs(b.x - a.x) for a, b in real_moves), 1),
        "average_move_distance": round(sum(move_distances) / len(move_distances), 1),
        "max_move_distance": round(max(move_distances), 1),
        "direction_changes": direction_changes,
        "average_hand_hold_size": round(sum(hand_hold_sizes) / len(hand_hold_sizes), 1),
        "min_hand_hold_size": round(min(hand_hold_sizes), 1),
        "foothold_ratio": round(foothold_ratio, 2),   # more available footholds = generally easier
        "crimp_count": hold_type_counts[HoldType.CRIMP],
        "sloper_count": hold_type_counts[HoldType.SLOPER],
        "avg_hold_difficulty": round(avg_hold_difficulty, 3),
    }
