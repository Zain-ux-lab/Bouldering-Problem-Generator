"""
main.py — the HTTP API. Deliberately thin: almost every line just
validates input and calls into service.py / db.py, which we already
tested independently above.

Run locally with:  uvicorn main:app --reload
Then visit http://127.0.0.1:8000/docs for FastAPI's automatic interactive
API documentation (this is a genuinely nice FastAPI feature worth knowing
about and mentioning in an interview).
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import db
import service

app = FastAPI(title="BoulderIQ API")

# Allows the browser-based frontend (running on a different port) to
# call this API. In a real production app you'd restrict this to your
# actual frontend's domain instead of "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    db.init_db()


# ---- Request/response schemas ----
# Pydantic models: FastAPI uses these to automatically validate incoming
# JSON (reject bad requests with a clear error) and to generate docs.

class GenerateRequest(BaseModel):
    angle_deg: int = Field(default=40, description="Wall angle: 40 or 45")
    min_moves: int = Field(default=6, ge=3, le=20)
    max_moves: int = Field(default=10, ge=3, le=20)


class PredictRequest(BaseModel):
    num_moves: int
    vertical_gain: float
    horizontal_movement: float
    average_move_distance: float
    max_move_distance: float
    direction_changes: int
    average_hand_hold_size: float
    min_hand_hold_size: float
    foothold_ratio: float
    crimp_count: int
    sloper_count: int
    avg_hold_difficulty: float


# ---- Endpoints ----

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/wall")
def get_wall(angle_deg: int = 40):
    if angle_deg not in (40, 45):
        raise HTTPException(status_code=400, detail="angle_deg must be 40 or 45")
    return service.get_wall_holds_json(angle_deg)


@app.post("/generate")
def generate(req: GenerateRequest):
    if req.angle_deg not in (40, 45):
        raise HTTPException(status_code=400, detail="angle_deg must be 40 or 45")
    if req.min_moves > req.max_moves:
        raise HTTPException(status_code=400, detail="min_moves cannot exceed max_moves")

    result = service.generate_and_save(
        angle_deg=req.angle_deg, min_moves=req.min_moves, max_moves=req.max_moves
    )
    if result is None:
        raise HTTPException(
            status_code=422,
            detail="Could not generate a valid problem with these constraints -- try a wider move range",
        )
    return result


@app.post("/predict")
def predict(req: PredictRequest):
    score, grade = service.predict_difficulty(req.model_dump())
    return {"predicted_difficulty": score, "estimated_grade": grade}


@app.get("/problems")
def list_problems(limit: int = 50):
    return db.list_problems(limit=limit)


@app.get("/problems/{problem_id}")
def get_problem(problem_id: int):
    problem = db.get_problem(problem_id)
    if problem is None:
        raise HTTPException(status_code=404, detail=f"No problem with id {problem_id}")
    return problem
