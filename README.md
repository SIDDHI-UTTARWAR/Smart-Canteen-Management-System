# 🍽️ Smart Canteen Management System

A college mini-project: a full working web app for managing a canteen —
admin login, food menu, orders & billing, inventory, customers, sales
reports, and an **AI-powered food demand prediction** module (scikit-learn
Random Forest).

**Stack:** Python, Flask, SQLite (zero-config), Bootstrap 5, Chart.js,
scikit-learn / pandas / numpy / joblib.

---

## 📁 Project Structure

```
Smart_Canteen/
├── app.py                 # Flask app & all routes
├── db.py                  # SQLite connection + auto table creation & seed data
├── schema.sql             # Database schema
├── requirements.txt
├── ml/
│   ├── generate_dataset.py   # builds ml/dataset.csv (sample sales history)
│   ├── train_model.py        # trains & compares ML models, saves best one
│   ├── prediction.py         # loads model, used by the Predict page
│   ├── dataset.csv           # (already generated)
│   └── demand_model.joblib   # (already trained)
├── templates/              # all HTML pages (Jinja2 + Bootstrap 5)
└── static/
    ├── css/style.css
    └── js/main.js
```

---

## ▶️ How to Run in VS Code

1. **Open the folder** `Smart_Canteen` in VS Code.
2. **Open a terminal** in VS Code: `Terminal → New Terminal`.
3. *(Recommended)* Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS/Linux
   ```
4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
5. *(Optional — already done for you, but you can redo it)*
   Regenerate the dataset & retrain the AI model:
   ```bash
   python ml/generate_dataset.py
   python ml/train_model.py
   ```
6. **Run the app:**
   ```bash
   python app.py
   ```
7. Open your browser at **http://127.0.0.1:5000**

### 🔑 Default Login
- Username: `admin`
- Password: `admin123`

The database (`canteen.db`) and demo data (sample food items, customers,
inventory) are created automatically the first time you run the app.

---

## ✨ Features

- **Secure Admin Login** — hashed passwords (Werkzeug), session-based auth
- **Dashboard** — revenue, orders, customers, low-stock alerts, popular
  items, bar/line/pie charts (Chart.js)
- **Food Management** — add/edit/delete menu items, stock, price, status,
  search
- **New Order + Billing** — interactive menu with live cart, auto GST (5%),
  discount, printable invoice, automatic stock deduction
- **Inventory Management** — track ingredients, low-stock alerts, update
  stock
- **Customer Management** — customer list + full order history & spending
- **Reports** — daily sales report + CSV export
- **AI Food Demand Prediction** — enter day/weather/temperature/festival/
  holiday/time-slot → Random Forest model predicts expected orders and how
  much of each food item to prepare, with a chart
- **Modern UI** — sidebar dashboard, dark mode toggle, toast notifications,
  fully responsive (mobile-friendly)

---

## 🤖 About the AI Model

`ml/train_model.py` trains and compares three models — **Linear
Regression**, **Decision Tree**, and **Random Forest** — using MAE, RMSE
and R² on a held-out test split, then saves the Random Forest pipeline
(the one used in production) with `joblib`. The dataset
(`ml/dataset.csv`) contains synthetic but realistic historical sales
records (Date, Day, Weather, Temperature, Festival, Holiday, Time Slot,
Food Name, Quantity Sold, Orders, Revenue).

---

## 🛠️ Switching to MySQL (optional)

This project uses SQLite by default so it runs instantly with no server
setup — ideal for a viva/demo. If your project guidelines require MySQL,
`schema.sql` is 95% MySQL-compatible (just change `AUTOINCREMENT` →
`AUTO_INCREMENT`), and you'd swap `db.py`'s `sqlite3.connect(...)` for a
`PyMySQL`/`mysql-connector` connection using the same SQL queries.

---

## 📸 Suggested Demo Flow (for your viva)

1. Log in → show Dashboard with charts.
2. Food Management → add a new item, edit price, search.
3. New Order → add items to cart, place order → auto-generated invoice.
4. Inventory → show low-stock alert.
5. Customers → view a customer's order history.
6. Reports → export CSV.
7. AI Demand Prediction → pick "Saturday, Rainy, Lunch, Festival = Yes" and
   show the predicted order count + which foods to prepare more of.
