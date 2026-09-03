"""
train_model.py — trains and compares models to predict a climbing
problem's synthetic difficulty score from its features.

Same core pattern as the diabetes project: load data -> train/test split
-> train multiple models -> compare -> save the best one.
"""

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

df = pd.read_csv("../backend/dataset.csv")

# wall_angle is constant (only 40 degrees generated so far) -- a
# constant column carries zero predictive information, so we drop it.
# This is a genuine current limitation: the model has never seen how
# angle affects difficulty. Noted here rather than hidden.
FEATURE_COLUMNS = [
    "num_moves", "vertical_gain", "horizontal_movement",
    "average_move_distance", "max_move_distance", "direction_changes",
    "average_hand_hold_size", "min_hand_hold_size", "foothold_ratio",
    "crimp_count", "sloper_count", "avg_hold_difficulty",
]

X = df[FEATURE_COLUMNS]
y = df["difficulty_score"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Training on {len(X_train)} problems, testing on {len(X_test)} held-out problems\n")


def evaluate(name, model):
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = mean_squared_error(y_test, preds) ** 0.5
    r2 = r2_score(y_test, preds)
    print(f"{name:<20} MAE={mae:.3f}   RMSE={rmse:.3f}   R²={r2:.3f}")
    return model, r2


results = {}

# Baseline: simplest possible model, a straight line through feature-space
lr = LinearRegression()
results["Linear Regression"] = evaluate("Linear Regression", lr)

# Stronger model: an ensemble of decision trees, can capture non-linear
# patterns the linear model can't (e.g. "direction changes only matter
# a lot when reach is also high" -- an interaction effect)
rf = RandomForestRegressor(n_estimators=200, random_state=42)
results["Random Forest"] = evaluate("Random Forest", rf)

# Pick the best model by R² and save it for the API to load later
best_name = max(results, key=lambda k: results[k][1])
best_model = results[best_name][0]
print(f"\nBest model: {best_name}")

# Feature importance (Random Forest only) -- which features actually
# drove predictions the most
if best_name == "Random Forest":
    importances = pd.Series(best_model.feature_importances_, index=FEATURE_COLUMNS)
    importances = importances.sort_values(ascending=False)
    print("\nTop 5 most important features:")
    print(importances.head(5))

joblib.dump(best_model, "difficulty_model.pkl")
print(f"\nSaved {best_name} to difficulty_model.pkl")
