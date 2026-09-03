"""
wall.py — the core data model for a Tension-Board-style climbing wall.

Real-world reference: standard Tension Board is 8ft x 10ft (244cm x 305cm),
adjustable to angles between 20-50 degrees (40 is the standard baseline,
45 also very common), with a SYMMETRIC, MIRRORED hold layout — meaning
the board is split into a left half and a right half, and every hold on
the left has a mirrored twin on the right in the same relative position.

This symmetry isn't just cosmetic — it's functional: it lets climbers
train the same move on both their left and right side, and it's the
defining feature that makes a Tension Board different from a generic
spray wall.
"""

from dataclasses import dataclass
from enum import Enum


class HoldType(Enum):
    """The kinds of climbing holds we support in the MVP."""
    JUG = "jug"          # big, easy to hold
    CRIMP = "crimp"       # small edge, fingertips only
    SLOPER = "sloper"     # rounded, relies on friction not grip
    FOOTHOLD = "foothold"  # small, used for feet only


class Side(Enum):
    LEFT = "left"
    RIGHT = "right"


@dataclass
class Hold:
    """
    A single climbing hold on the wall.

    x, y: position in centimeters, measured from the bottom-left corner
          of the ENTIRE wall (so left-half holds have small x, right-half
          holds have large x).
    side: which half of the (symmetric) board this hold belongs to.
    mirror_id: the id of this hold's mirrored twin on the other side.
               None only for holds placed exactly on the centerline.
    """
    id: int
    x: float
    y: float
    hold_type: HoldType
    size: float           # diameter in cm, roughly
    orientation: float    # degrees, 0 = facing straight up/out
    side: Side
    mirror_id: int | None = None


@dataclass
class Wall:
    """
    A Tension-Board-style climbing wall.

    width_cm / height_cm: real dimensions, based on the standard 8ft x 10ft board.
    angle_deg: must be 40 or 45 for our MVP (the two most common Tension Board angles).
    holds: every Hold placed on this wall.
    """
    width_cm: float
    height_cm: float
    angle_deg: int
    holds: list

    VALID_ANGLES = (40, 45)

    def __post_init__(self):
        if self.angle_deg not in self.VALID_ANGLES:
            raise ValueError(
                f"angle_deg must be one of {self.VALID_ANGLES}, got {self.angle_deg}"
            )

    @property
    def centerline_x(self):
        """The x-coordinate of the vertical line splitting the wall into symmetric halves."""
        return self.width_cm / 2

    def holds_on(self, side: Side):
        return [h for h in self.holds if h.side == side]

    def get_hold(self, hold_id: int):
        for h in self.holds:
            if h.id == hold_id:
                return h
        raise KeyError(f"No hold with id {hold_id}")
