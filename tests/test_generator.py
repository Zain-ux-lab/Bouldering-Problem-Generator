"""
test_generator.py — tests that generated problems actually satisfy the
constraints they're supposed to (per project brief section 17: "Generated
problem must satisfy maximum reach constraint", "must contain the
requested number of moves", "Start and finish must exist").

v2: paths now start with a TWO-HAND start position (path[0:2]), and
never include footholds (footholds are suggested separately).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from generate_wall import build_wall
from generator.generator import generate_problem, suggest_footholds
from generator.constraints import distance
from models.wall import HoldType


def test_generated_problem_has_moves_in_requested_range():
    wall = build_wall(angle_deg=40)
    path = generate_problem(wall, min_moves=6, max_moves=10)
    assert path is not None
    num_moves = len(path) - 2  # exclude the 2-hold start position
    assert 6 <= num_moves <= 10


def test_generated_problem_respects_max_reach():
    wall = build_wall(angle_deg=40)
    max_reach = 90
    path = generate_problem(wall, min_moves=6, max_moves=10, max_reach_cm=max_reach)
    assert path is not None

    holds = [wall.get_hold(hid) for hid in path]
    for a, b in zip(holds, holds[1:]):
        assert distance(a, b) <= max_reach


def test_real_moves_always_move_upward():
    """Every move AFTER the two-hand start should go strictly up the wall."""
    wall = build_wall(angle_deg=40)
    path = generate_problem(wall, min_moves=6, max_moves=10)
    holds = [wall.get_hold(hid) for hid in path]
    real_moves = list(zip(holds[1:], holds[2:]))  # skip the start-pair span
    for a, b in real_moves:
        assert b.y > a.y


def test_generated_problem_has_no_repeated_holds():
    wall = build_wall(angle_deg=40)
    path = generate_problem(wall, min_moves=6, max_moves=10)
    assert len(path) == len(set(path))  # every hold used at most once


def test_generated_problem_has_start_and_finish():
    wall = build_wall(angle_deg=40)
    path = generate_problem(wall, min_moves=6, max_moves=10)
    assert path is not None
    assert len(path) >= 3  # 2-hold start + at least 1 more hold


def test_start_is_two_distinct_nearby_holds():
    """A real climber starts on two hands, not one."""
    wall = build_wall(angle_deg=40)
    path = generate_problem(wall, min_moves=6, max_moves=10)
    holds = [wall.get_hold(hid) for hid in path]
    assert holds[0].id != holds[1].id
    assert distance(holds[0], holds[1]) <= 55  # a plausible hand span


def test_no_footholds_in_hand_path():
    """Footholds are for feet, not hands -- they must never appear in the path."""
    wall = build_wall(angle_deg=40)
    path = generate_problem(wall, min_moves=6, max_moves=10)
    holds = [wall.get_hold(hid) for hid in path]
    assert all(h.hold_type != HoldType.FOOTHOLD for h in holds)


def test_foothold_suggestions_are_valid_footholds():
    wall = build_wall(angle_deg=40)
    path = generate_problem(wall, min_moves=6, max_moves=10)
    suggestions = suggest_footholds(wall, path)
    assert len(suggestions) == len(path)
    for fid in suggestions:
        if fid is not None:
            assert wall.get_hold(fid).hold_type == HoldType.FOOTHOLD
