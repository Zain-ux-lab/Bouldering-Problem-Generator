"""
constraints.py — defines what counts as a "valid move" between two holds.

This is a deliberately SIMPLIFIED model of climbing physics (per the
project's own scope rules -- no biomechanics, no finger strength). We
reduce "can a climber move from hold A to hold B" down to two measurable
rules:

1. DISTANCE: the straight-line distance between A and B must be within
   a min/max reach range (too close = pointless move, too far = impossible).
2. DIRECTION: B must be higher up the wall than A (climbing goes up).
   This is a simplification -- real climbing has lateral and even
   downward moves -- but it keeps the MVP's graph well-behaved (no
   infinite loops going back and forth between two holds).
"""

import math


def distance(hold_a, hold_b):
    """Straight-line (Euclidean) distance between two holds, in cm."""
    return math.hypot(hold_b.x - hold_a.x, hold_b.y - hold_a.y)


def is_valid_move(hold_a, hold_b, min_reach_cm=15, max_reach_cm=90):
    """
    Can a climber plausibly move from hold_a to hold_b under our
    simplified rules?
    """
    if hold_b.y <= hold_a.y:
        return False  # must move upward

    d = distance(hold_a, hold_b)
    return min_reach_cm <= d <= max_reach_cm
