"""
service.py — the actual application logic, deliberately kept independent
of FastAPI. main.py will just be a thin HTTP wrapper around these
functions. This separation means:
  1. I can test this logic directly (no server needed)
  2. If we ever swapped FastAPI for something else, this file wouldn't change
"""

import joblib
import pandas as pd
from pathlib import Path

from generate_wall import build_wall
from generator.generator import generate_problem, suggest_footholds
from generator.features import extract_features
from build_dataset import grade_from_score
import db

MODEL_PATH = Path(__file__).parent / "difficulty_model.pkl"
FEATURE_COLUMNS = [
    "num_moves", "vertical_gain", "horizontal_movement",
    "average_move_distance", "max_move_distance", "direction_changes",
    "average_hand_hold_size", "min_hand_hold_size", "foothold_ratio",
    "crimp_count", "sloper_count", "avg_hold_difficulty",
]

_model = None
_wall_cache = {}  # angle_deg -> Wall, so we don't rebuild the wall on every request


def get_model():
    """Lazily load the trained model once, reuse it after that (loading from disk is slow)."""
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def get_wall(angle_deg=40):
    if angle_deg not in _wall_cache:
        _wall_cache[angle_deg] = build_wall(angle_deg=angle_deg)
    return _wall_cache[angle_deg]


def get_wall_holds_json(angle_deg=40):
    """Returns every hold on the wall as plain JSON-friendly dicts (for the frontend to draw)."""
    wall = get_wall(angle_deg)
    return {
        "width_cm": wall.width_cm,
        "height_cm": wall.height_cm,
        "angle_deg": wall.angle_deg,
        "holds": [
            {
                "id": h.id,
                "x": h.x,
                "y": h.y,
                "hold_type": h.hold_type.value,
                "size": h.size,
                "side": h.side.value,
            }
            for h in wall.holds
        ],
    }


def predict_difficulty(features: dict):
    """Takes a feature dict, returns (difficulty_score, grade)."""
    model = get_model()
    row = pd.DataFrame([[features[col] for col in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)
    score = float(model.predict(row)[0])
    grade = grade_from_score(score)
    return round(score, 2), grade


def generate_and_save(angle_deg=40, min_moves=6, max_moves=10):
    """
    The full pipeline for one request:
    generate a problem -> extract features -> predict difficulty -> save it.
    Returns the saved problem dict, or None if generation failed.
    """
    wall = get_wall(angle_deg)
    path = generate_problem(wall, min_moves=min_moves, max_moves=max_moves)
    if path is None:
        return None

    features = extract_features(wall, path)
    score, grade = predict_difficulty(features)
    foot_suggestions = suggest_footholds(wall, path)

    problem_id = db.save_problem(
        wall_angle=angle_deg,
        hold_path=path,
        foot_suggestions=foot_suggestions,
        features=features,
        predicted_difficulty=score,
        predicted_grade=grade,
    )

    return db.get_problem(problem_id)
