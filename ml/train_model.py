"""
Trains a Random Forest Regressor to predict expected Orders, comparing it
against Linear Regression and Decision Tree. Saves the best pipeline with
joblib. Run: python ml/train_model.py
"""
import os
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "demand_model.joblib")

CATEGORICAL = ["Day", "Weather", "Festival", "Holiday", "Time Slot"]
NUMERIC = ["Temperature"]
TARGET = "Orders"


def main():
    df = pd.read_csv(DATASET_PATH).drop_duplicates(subset=["Date", "Time Slot"]).dropna()
    X = df[CATEGORICAL + NUMERIC]
    y = df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pre = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL)],
                             remainder="passthrough")

    models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(max_depth=8, random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=150, max_depth=10, random_state=42),
    }

    best_pipe = None
    for name, model in models.items():
        pipe = Pipeline([("pre", pre), ("model", model)])
        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        r2 = r2_score(y_test, preds)
        print(f"{name:20s} | MAE={mae:6.2f}  RMSE={rmse:6.2f}  R2={r2:5.3f}")
        if name == "Random Forest":
            best_pipe = pipe

    joblib.dump(best_pipe, MODEL_PATH)
    print(f"\nSaved production model (Random Forest) -> {MODEL_PATH}")


if __name__ == "__main__":
    main()
