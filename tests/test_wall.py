"""
test_wall.py — tests for the wall/hold data model and symmetric generation.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from generate_wall import build_wall
from models.wall import Side


def test_wall_has_correct_real_world_dimensions():
    wall = build_wall(angle_deg=40)
    assert wall.width_cm == 244   # 8ft
    assert wall.height_cm == 305  # 10ft


def test_invalid_angle_rejected():
    with pytest.raises(ValueError):
        build_wall(angle_deg=37)  # not 40 or 45


def test_wall_is_symmetric():
    """Every left-side hold must have a mirror on the right at width - x."""
    wall = build_wall(angle_deg=40)
    left_holds = wall.holds_on(Side.LEFT)
    assert len(left_holds) > 0

    for h in left_holds:
        mirror = wall.get_hold(h.mirror_id)
        assert mirror.side == Side.RIGHT
        assert abs((wall.width_cm - h.x) - mirror.x) < 0.01
        assert abs(h.y - mirror.y) < 0.01  # same height


def test_equal_holds_each_side():
    wall = build_wall(angle_deg=40)
    assert len(wall.holds_on(Side.LEFT)) == len(wall.holds_on(Side.RIGHT))
