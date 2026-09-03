"""
test_features.py — tests for feature extraction from a generated path.

Includes a REGRESSION TEST for the real foothold-sizing bug found during
development: footholds are deliberately small, and including them in the
same size average as hand holds was incorrectly making foothold-heavy
problems look HARDER instead of easier. This test guarantees that bug
can never silently return.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from generate_wall import build_wall
from generator.generator import generate_problem
from generator.features import extract_features
from build_dataset import synthetic_difficulty


def test_features_include_expected_keys():
    wall = build_wall(angle_deg=40)
    path = generate_problem(wall, min_moves=6, max_moves=10)
    features = extract_features(wall, path)

    expected_keys = {
        "wall_angle", "num_moves", "vertical_gain", "horizontal_movement",
        "average_move_distance", "max_move_distance", "direction_changes",
        "average_hand_hold_size", "min_hand_hold_size", "foothold_ratio",
        "crimp_count", "sloper_count", "avg_hold_difficulty",
    }
    assert expected_keys.issubset(features.keys())


def test_num_moves_excludes_start_pair():
    wall = build_wall(angle_deg=40)
    path = generate_problem(wall, min_moves=6, max_moves=10)
    features = extract_features(wall, path)
    assert features["num_moves"] == len(path) - 2  # 2-hold start excluded


def test_more_footholds_means_lower_difficulty_score():
    """
    REGRESSION TEST for the real bug found during development:
    a problem with MORE footholds should score EASIER, not harder,
    because footholds provide better foot support. Footholds must not
    drag down "average_hand_hold_size" (they're excluded from it) and
    foothold_ratio must have a NEGATIVE effect on difficulty.
    """
    base_features = {
        "num_moves": 8, "vertical_gain": 200, "horizontal_movement": 150,
        "average_move_distance": 55, "max_move_distance": 80, "direction_changes": 3,
        "average_hand_hold_size": 10, "min_hand_hold_size": 5,
        "crimp_count": 2, "sloper_count": 1, "avg_hold_difficulty": 0.5,
    }

    low_footholds = {**base_features, "foothold_ratio": 0.0}
    high_footholds = {**base_features, "foothold_ratio": 0.5}

    score_low = synthetic_difficulty(low_footholds)
    score_high = synthetic_difficulty(high_footholds)

    assert score_high < score_low, (
        f"More footholds should mean EASIER (lower score), got "
        f"low_footholds={score_low}, high_footholds={score_high}"
    )
