# BoulderIQ

A backend-heavy platform that algorithmically generates Tension-Board-style bouldering problems and predicts their difficulty using machine learning.

## Status: Days 1-10 of a 14-day MVP plan complete

- ✅ **Wall & hold data model** — symmetric, mirrored layout based on real Tension Board dimensions (8ft × 10ft, 40°/45° angles)
- ✅ **Problem generator** — reachability graph + DFS/backtracking search to generate valid, climbable-looking sequences
- ✅ **Feature engineering** — 12 numerical features extracted per problem (reach distances, direction changes, hold quality, foothold ratio, etc.)
- ✅ **Synthetic dataset** — 500 generated problems with a transparent, hand-written difficulty formula
- ✅ **ML pipeline** — trained and compared Linear Regression vs. Random Forest
- ✅ **REST API** — FastAPI backend exposing `/generate`, `/predict`, `/problems`, `/health`
- ⬜ Web frontend — not built yet
- ⬜ Docker — not built yet
- ⬜ Cloud deployment — optional, not attempted yet

## Honest limitations (worth reading before an interview)

1. **The training data is synthetic, not real climber data.** The model predicts *our own* difficulty formula, not objective human climbing difficulty. A real dataset is genuinely reachable via the open-source [`boardlib`](https://pypi.org/project/boardlib/) tool, which can pull real Kilter/Tension Board hold layouts and real community-logged ascent grades — integrating it is a natural next step, scoped out of this MVP for time.
2. **Linear Regression scored a near-perfect R² (1.000) on the synthetic data.** This isn't an impressive result — it's expected, because the synthetic difficulty label is itself a linear formula of the same features the model trains on. It's a useful sanity check that the pipeline works correctly end-to-end, not evidence of real predictive power. The real test comes once real (noisier, non-linear) data replaces the synthetic label.
3. **`wall_angle` is currently a constant** (only 40° walls have been generated so far), so the model has never actually learned how angle affects difficulty. Needs 45°-angle problems generated too.
4. **The model conflates hand holds and footholds' roles into one sequential path.** Real climbing uses hands and feet somewhat independently; this is a deliberate simplification, not an oversight (see project scope notes).
5. A real foothold-vs-hand-hold sizing bug was found and fixed during development — footholds were dragging the "average hold size" down and incorrectly increasing predicted difficulty, when more footholds should make a problem easier. Fixed by separating hand-hold size from foothold presence as distinct features.

## Architecture

```
Browser (not built yet)
        |
        v
  FastAPI backend (main.py)
        |
   +----+----+
   |         |
   v         v
Generator   ML Model
(graph +    (trained on
backtracking) synthetic data)
   |         |
   +----+----+
        |
        v
   SQLite database
```

## Run it yourself

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/docs for interactive API documentation.

To regenerate the dataset or retrain the model:
```bash
python3 build_dataset.py      # from backend/
cd ../ml && python3 train_model.py
```

## Project structure

```
boulderiq/
├── backend/
│   ├── models/wall.py           # Wall and Hold data model
│   ├── generate_wall.py         # symmetric hold layout generation
│   ├── generator/
│   │   ├── constraints.py       # what counts as a valid move
│   │   ├── graph.py             # builds the reachability graph
│   │   ├── generator.py         # DFS/backtracking problem search
│   │   └── features.py          # feature extraction
│   ├── build_dataset.py         # synthetic dataset + difficulty formula
│   ├── db.py                    # SQLite storage layer
│   ├── service.py               # core logic (generate + predict + save)
│   ├── main.py                  # FastAPI HTTP layer
│   └── requirements.txt
└── ml/
    └── train_model.py           # model training + comparison
```

## What I'd improve next

- Integrate real problem/grade data via `boardlib`
- Generate problems across both 40° and 45° walls
- Separate hand-hold and foothold sequences properly instead of one merged path
- Web frontend with visual hold rendering
- Docker + cloud deployment
