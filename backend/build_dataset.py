"""
build_dataset.py — generates many problems, extracts features for each,
and assigns each one a SYNTHETIC difficulty score using a transparent,
hand-written formula.

HONESTY NOTE (carried over from the project brief): this difficulty
score is OUR OWN definition, not real climbers' opinions. The ML model
we train later will learn to predict THIS formula, not objective human
difficulty. That's a real, explainable limitation -- worth stating
directly in the README and in an interview, not hidden.
"""

import pandas as pd
from generate_wall import build_wall
from generator.generator import generate_problem
from generator.features import extract_features


def synthetic_difficulty(features):
    """
    A transparent, rule-based scoring formula (0-5+ scale, uncapped
    before clipping). Each term is a plausible, explainable contributor
    to difficulty -- e.g. bigger reaches, more crimps, more direction
    changes should all push difficulty up.

    Weights are our own design choice -- not derived from real data.
    """
    score = (
        0.030 * features["max_move_distance"]
        + 0.020 * features["average_move_distance"]
        + 0.400 * features["direction_changes"]
        + 3.000 * features["avg_hold_difficulty"]
        - 0.080 * features["average_hand_hold_size"]   # bigger HAND holds = easier
        - 1.500 * features["foothold_ratio"]            # more footholds = easier (fixed)
        + 0.100 * features["num_moves"]
    )
    return round(max(0, min(score, 9)), 2)   # clip to a sane 0-9 range


def grade_from_score(score):
    """Convert the numeric score into a V-grade-style label, purely for readability."""
    v_grade = round(score * 0.9)  # rough mapping, our own choice
    return f"V{max(0, v_grade)}"


def build_dataset(n_problems=500, angle_deg=40):
    wall = build_wall(angle_deg=angle_deg)
    rows = []

    attempts = 0
    while len(rows) < n_problems and attempts < n_problems * 5:
        attempts += 1
        path = generate_problem(wall, min_moves=5, max_moves=12)
        if path is None:
            continue

        features = extract_features(wall, path)
        score = synthetic_difficulty(features)
        features["difficulty_score"] = score
        features["grade"] = grade_from_score(score)
        rows.append(features)

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = build_dataset(n_problems=500)
    print(f"Generated {len(df)} problems")
    print("\nFirst 5:")
    print(df.head())
    print("\nDifficulty score distribution:")
    print(df["difficulty_score"].describe())
    print("\nGrade distribution:")
    print(df["grade"].value_counts().sort_index())

    df.to_csv("dataset.csv", index=False)
    print("\nSaved dataset.csv")
