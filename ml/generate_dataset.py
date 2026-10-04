"""
Generates ml/dataset.csv — synthetic canteen sales history used to train
the demand-prediction model. Run once: python ml/generate_dataset.py
"""
import random
import csv
from datetime import datetime, timedelta

random.seed(42)

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEATHER = ["Sunny", "Rainy", "Cloudy", "Cold", "Hot"]
TIME_SLOTS = ["Breakfast", "Lunch", "Snacks", "Dinner"]
FOOD_PRICE = {
    "Veg Thali": 60, "Chicken Biryani": 120, "Masala Dosa": 45, "Samosa": 15,
    "Paneer Roll": 55, "Cold Coffee": 40, "Tea": 10, "Sandwich": 35,
}


def base_demand(day, weather, slot, festival, holiday, temp):
    d = 25
    if day in ("Saturday", "Sunday"):
        d += 12
    if slot == "Lunch":
        d += 20
    elif slot == "Snacks":
        d += 10
    if weather == "Rainy":
        d += 8
    if festival == "Yes":
        d += 15
    if holiday == "Yes":
        d -= 8
    d += random.randint(-6, 6)
    return max(d, 5)


def generate(num_days=45, out_path="ml/dataset.csv"):
    rows = []
    start = datetime(2026, 1, 1)
    for i in range(num_days):
        date = start + timedelta(days=i)
        day = DAYS[date.weekday()]
        weather = random.choice(WEATHER)
        temp = round(random.uniform(15, 38), 1)
        festival = "Yes" if random.random() < 0.08 else "No"
        holiday = "Yes" if random.random() < 0.1 else "No"
        for slot in TIME_SLOTS:
            orders = base_demand(day, weather, slot, festival, holiday, temp)
            foods = random.sample(list(FOOD_PRICE), k=3)
            for food in foods:
                qty = max(1, int(orders * random.uniform(0.2, 0.4)))
                revenue = qty * FOOD_PRICE[food]
                rows.append([date.strftime("%Y-%m-%d"), day, weather, temp,
                             festival, holiday, slot, food, qty, orders, revenue])

    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Date", "Day", "Weather", "Temperature", "Festival", "Holiday",
                     "Time Slot", "Food Name", "Quantity Sold", "Orders", "Revenue"])
        w.writerows(rows)
    print(f"Generated {len(rows)} rows -> {out_path}")


if __name__ == "__main__":
    generate()
