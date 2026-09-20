"""
db.py — SQLite storage for generated climbing problems.

Kept deliberately separate from the API layer (main.py) so it can be
tested and understood on its own, without needing FastAPI running.
"""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "boulderiq.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name, e.g. row["grade"]
    return conn


def init_db():
    """Creates the problems table if it doesn't already exist. Safe to call every startup."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wall_angle INTEGER NOT NULL,
            hold_path TEXT NOT NULL,       -- JSON list of hand-hold ids, in order
            start_feet TEXT NOT NULL,      -- JSON list of required starting foothold ids
            foot_suggestions TEXT NOT NULL, -- JSON list, one suggested foothold id (or null) per hand hold
            features TEXT NOT NULL,        -- JSON dict of computed features
            predicted_difficulty REAL NOT NULL,
            predicted_grade TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_problem(wall_angle, hold_path, start_feet, foot_suggestions, features, predicted_difficulty, predicted_grade):
    """Stores one generated problem, returns its new id."""
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO problems (wall_angle, hold_path, start_feet, foot_suggestions, features, predicted_difficulty, predicted_grade)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (wall_angle, json.dumps(hold_path), json.dumps(start_feet), json.dumps(foot_suggestions), json.dumps(features), predicted_difficulty, predicted_grade),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_problem(problem_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM problems WHERE id = ?", (problem_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    return _row_to_dict(row)


def list_problems(limit=50):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM problems ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def _row_to_dict(row):
    return {
        "id": row["id"],
        "wall_angle": row["wall_angle"],
        "hold_path": json.loads(row["hold_path"]),
        "start_feet": json.loads(row["start_feet"]),
        "foot_suggestions": json.loads(row["foot_suggestions"]),
        "features": json.loads(row["features"]),
        "predicted_difficulty": row["predicted_difficulty"],
        "predicted_grade": row["predicted_grade"],
        "created_at": row["created_at"],
    }
