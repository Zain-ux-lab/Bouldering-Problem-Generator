"""
test_db.py — tests for SQLite storage. Uses a temporary, isolated
database file per test run so tests never interfere with your real
boulderiq.db or each other.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import tempfile
import pytest
import db


@pytest.fixture
def temp_db(monkeypatch):
    """Point db.py at a fresh temporary file for the duration of one test."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr(db, "DB_PATH", path)
    db.init_db()
    yield
    os.remove(path)


def test_save_and_get_problem(temp_db):
    problem_id = db.save_problem(
        wall_angle=40,
        hold_path=[1, 2, 3],
        features={"num_moves": 2},
        predicted_difficulty=5.5,
        predicted_grade="V5",
    )
    fetched = db.get_problem(problem_id)

    assert fetched is not None
    assert fetched["wall_angle"] == 40
    assert fetched["hold_path"] == [1, 2, 3]
    assert fetched["predicted_grade"] == "V5"


def test_get_nonexistent_problem_returns_none(temp_db):
    assert db.get_problem(99999) is None


def test_list_problems_returns_saved_ones(temp_db):
    db.save_problem(40, [1, 2], {}, 4.0, "V4")
    db.save_problem(40, [3, 4], {}, 6.0, "V6")

    problems = db.list_problems()
    assert len(problems) == 2
    grades = {p["predicted_grade"] for p in problems}
    assert grades == {"V4", "V6"}
