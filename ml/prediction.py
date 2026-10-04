"""
Loads the trained model and predicts expected orders + per-food demand.
"""
import os
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "demand_model.joblib")
DATASET_PATH = os.path.join(BASE_DIR, "dataset.csv")

_model = None


def get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError("Model not trained. Run: python ml/train_model.py")
        _model = joblib.load(MODEL_PATH)
    return _model


def predict_demand(day, weather, temperature, festival, holiday, time_slot):
    model = get_model()
    X = pd.DataFrame([{
        "Day": day, "Weather": weather, "Festival": festival,
        "Holiday": holiday, "Time Slot": time_slot, "Temperature": float(temperature),
    }])
    predicted_orders = max(0, round(float(model.predict(X)[0])))

    df = pd.read_csv(DATASET_PATH)
    slot_df = df[df["Time Slot"] == time_slot]
    share = (slot_df.groupby("Food Name")["Quantity Sold"].sum() /
             slot_df["Quantity Sold"].sum()).sort_values(ascending=False)

    food_demand = [{"food": f, "quantity_to_prepare": max(1, round(predicted_orders * s))}
                   for f, s in share.items()]

    return {
        "predicted_orders": predicted_orders,
        "food_demand": food_demand,
        "high_demand_foods": [f["food"] for f in food_demand[:3]],
        "low_demand_foods": [f["food"] for f in food_demand[-2:]],
    }
