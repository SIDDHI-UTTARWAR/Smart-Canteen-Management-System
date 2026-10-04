"""
Smart Canteen Management System
--------------------------------
A compact Flask + SQLite web app with an admin dashboard, food/order/
billing/inventory/customer management, and an AI-powered food demand
prediction module (scikit-learn Random Forest).

Run:
    pip install -r requirements.txt
    l/generate_dataspython met.py   (already generated, but safe to re-run)
    python ml/train_model.py        (already trained, but safe to re-run)
    python app.py
Then open http://127.0.0.1:5000
Default login -> username: admin | password: admin123
"""
import os
import io
import csv
from datetime import datetime
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                    session, flash, send_file, jsonify)
from werkzeug.security import check_password_hash

from db import get_db, init_db
from ml.prediction import predict_demand

app = Flask(__name__)
app.secret_key = "smart-canteen-secret-key-2026"

GST_PERCENT = 5.0

init_db()


# ---------------------------------------------------------------- helpers
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "admin_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


@app.context_processor
def inject_globals():
    return {"now": datetime.now()}


# ------------------------------------------------------------- auth views
@app.route("/")
def index():
    return redirect(url_for("dashboard") if "admin_id" in session else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        db = get_db()
        admin = db.execute("SELECT * FROM admin WHERE username = ?", (username,)).fetchone()
        db.close()
        if admin and check_password_hash(admin["password_hash"], password):
            session["admin_id"] = admin["id"]
            session["admin_name"] = admin["full_name"]
            flash("Welcome back, " + admin["full_name"] + "!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# --------------------------------------------------------------- dashboard
@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    today = datetime.now().strftime("%Y-%m-%d")

    today_revenue = db.execute(
        "SELECT COALESCE(SUM(total_amount),0) AS t FROM orders WHERE order_date = ?", (today,)
    ).fetchone()["t"]
    total_orders = db.execute("SELECT COUNT(*) AS c FROM orders").fetchone()["c"]
    total_customers = db.execute("SELECT COUNT(*) AS c FROM customers").fetchone()["c"]
    total_food = db.execute("SELECT COUNT(*) AS c FROM food").fetchone()["c"]
    low_stock = db.execute(
        "SELECT * FROM inventory WHERE available_quantity <= minimum_stock"
    ).fetchall()

    popular = db.execute(
        "SELECT food_name, SUM(quantity) AS qty FROM order_items "
        "GROUP BY food_name ORDER BY qty DESC LIMIT 5"
    ).fetchall()

    weekly = db.execute(
        "SELECT order_date, SUM(total_amount) AS total FROM orders "
        "GROUP BY order_date ORDER BY order_date DESC LIMIT 7"
    ).fetchall()
    weekly = list(reversed(weekly))

    monthly = db.execute(
        "SELECT strftime('%Y-%m', order_date) AS month, SUM(total_amount) AS total "
        "FROM orders GROUP BY month ORDER BY month DESC LIMIT 6"
    ).fetchall()
    monthly = list(reversed(monthly))

    category_split = db.execute(
        "SELECT category, COUNT(*) AS c FROM food GROUP BY category"
    ).fetchall()

    db.close()
    return render_template(
        "dashboard.html",
        today_revenue=today_revenue, total_orders=total_orders,
        total_customers=total_customers, total_food=total_food,
        low_stock=low_stock, popular=popular, weekly=weekly,
        monthly=monthly, category_split=category_split,
    )


# ---------------------------------------------------------- food (Module 3)
@app.route("/food")
@login_required
def food_list():
    q = request.args.get("q", "").strip()
    db = get_db()
    if q:
        rows = db.execute(
            "SELECT * FROM food WHERE name LIKE ? OR category LIKE ? ORDER BY id DESC",
            (f"%{q}%", f"%{q}%"),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM food ORDER BY id DESC").fetchall()
    db.close()
    return render_template("food.html", foods=rows, q=q)


@app.route("/food/add", methods=["POST"])
@login_required
def food_add():
    name = request.form["name"].strip()
    category = request.form["category"].strip()
    price = float(request.form["price"])
    quantity = int(request.form["quantity"])
    status = request.form.get("status", "Available")
    db = get_db()
    db.execute(
        "INSERT INTO food (name, category, price, quantity, status) VALUES (?, ?, ?, ?, ?)",
        (name, category, price, quantity, status),
    )
    db.commit()
    db.close()
    flash(f'"{name}" added to the menu.', "success")
    return redirect(url_for("food_list"))


@app.route("/food/edit/<int:food_id>", methods=["POST"])
@login_required
def food_edit(food_id):
    name = request.form["name"].strip()
    category = request.form["category"].strip()
    price = float(request.form["price"])
    quantity = int(request.form["quantity"])
    status = request.form.get("status", "Available")
    db = get_db()
    db.execute(
        "UPDATE food SET name=?, category=?, price=?, quantity=?, status=? WHERE id=?",
        (name, category, price, quantity, status, food_id),
    )
    db.commit()
    db.close()
    flash("Food item updated.", "success")
    return redirect(url_for("food_list"))


@app.route("/food/delete/<int:food_id>")
@login_required
def food_delete(food_id):
    db = get_db()
    db.execute("DELETE FROM food WHERE id=?", (food_id,))
    db.commit()
    db.close()
    flash("Food item deleted.", "info")
    return redirect(url_for("food_list"))


# ------------------------------------------------------ orders (Module 4/5)
@app.route("/orders")
@login_required
def orders_list():
    db = get_db()
    rows = db.execute(
        "SELECT o.*, c.name AS customer_name FROM orders o "
        "JOIN customers c ON c.id = o.customer_id ORDER BY o.id DESC"
    ).fetchall()
    db.close()
    return render_template("orders.html", orders=rows)


@app.route("/orders/new", methods=["GET", "POST"])
@login_required
def order_new():
    db = get_db()
    if request.method == "POST":
        customer_name = request.form["customer_name"].strip()
        phone = request.form["phone"].strip()
        food_ids = request.form.getlist("food_id")
        quantities = request.form.getlist("quantity")

        if not food_ids:
            flash("Please add at least one item to the order.", "warning")
            return redirect(url_for("order_new"))

        customer = db.execute("SELECT * FROM customers WHERE phone=?", (phone,)).fetchone()
        if customer:
            customer_id = customer["id"]
        else:
            cur = db.execute(
                "INSERT INTO customers (name, phone) VALUES (?, ?)", (customer_name, phone)
            )
            customer_id = cur.lastrowid

        now = datetime.now()
        cur = db.execute(
            "INSERT INTO orders (customer_id, order_date, order_time, total_amount, status) "
            "VALUES (?, ?, ?, 0, 'Completed')",
            (customer_id, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")),
        )
        order_id = cur.lastrowid

        subtotal = 0.0
        for fid, qty in zip(food_ids, quantities):
            qty = int(qty)
            if qty <= 0:
                continue
            food = db.execute("SELECT * FROM food WHERE id=?", (fid,)).fetchone()
            if not food:
                continue
            line_total = food["price"] * qty
            subtotal += line_total
            db.execute(
                "INSERT INTO order_items (order_id, food_id, food_name, quantity, price_each) "
                "VALUES (?, ?, ?, ?, ?)",
                (order_id, fid, food["name"], qty, food["price"]),
            )
            # reduce stock automatically
            new_qty = max(0, food["quantity"] - qty)
            db.execute("UPDATE food SET quantity=? WHERE id=?", (new_qty, fid))

        gst_amount = round(subtotal * GST_PERCENT / 100, 2)
        discount_percent = float(request.form.get("discount", 0) or 0)
        discount_amount = round(subtotal * discount_percent / 100, 2)
        final_total = round(subtotal + gst_amount - discount_amount, 2)

        db.execute("UPDATE orders SET total_amount=? WHERE id=?", (final_total, order_id))
        db.execute(
            "INSERT INTO bills (order_id, subtotal, gst_percent, gst_amount, "
            "discount_percent, discount_amount, final_total, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (order_id, subtotal, GST_PERCENT, gst_amount, discount_percent,
             discount_amount, final_total, now.strftime("%Y-%m-%d %H:%M:%S")),
        )
        db.commit()
        db.close()
        flash("Order placed and bill generated!", "success")
        return redirect(url_for("bill_view", order_id=order_id))

    foods = db.execute("SELECT * FROM food WHERE status='Available' ORDER BY category, name").fetchall()
    db.close()
    return render_template("order_new.html", foods=foods, gst=GST_PERCENT)


@app.route("/bill/<int:order_id>")
@login_required
def bill_view(order_id):
    db = get_db()
    order = db.execute(
        "SELECT o.*, c.name AS customer_name, c.phone FROM orders o "
        "JOIN customers c ON c.id = o.customer_id WHERE o.id=?", (order_id,)
    ).fetchone()
    items = db.execute("SELECT * FROM order_items WHERE order_id=?", (order_id,)).fetchall()
    bill = db.execute("SELECT * FROM bills WHERE order_id=?", (order_id,)).fetchone()
    db.close()
    return render_template("bill.html", order=order, items=items, bill=bill)


# ---------------------------------------------------------- inventory (M6)
@app.route("/inventory")
@login_required
def inventory_list():
    db = get_db()
    rows = db.execute("SELECT * FROM inventory ORDER BY id DESC").fetchall()
    db.close()
    return render_template("inventory.html", items=rows)


@app.route("/inventory/add", methods=["POST"])
@login_required
def inventory_add():
    db = get_db()
    db.execute(
        "INSERT INTO inventory (ingredient_name, available_quantity, unit, minimum_stock) "
        "VALUES (?, ?, ?, ?)",
        (request.form["ingredient_name"], float(request.form["available_quantity"]),
         request.form["unit"], float(request.form["minimum_stock"])),
    )
    db.commit()
    db.close()
    flash("Ingredient added to inventory.", "success")
    return redirect(url_for("inventory_list"))


@app.route("/inventory/update/<int:item_id>", methods=["POST"])
@login_required
def inventory_update(item_id):
    db = get_db()
    db.execute(
        "UPDATE inventory SET available_quantity=?, minimum_stock=? WHERE id=?",
        (float(request.form["available_quantity"]), float(request.form["minimum_stock"]), item_id),
    )
    db.commit()
    db.close()
    flash("Stock updated.", "success")
    return redirect(url_for("inventory_list"))


@app.route("/inventory/delete/<int:item_id>")
@login_required
def inventory_delete(item_id):
    db = get_db()
    db.execute("DELETE FROM inventory WHERE id=?", (item_id,))
    db.commit()
    db.close()
    flash("Ingredient removed.", "info")
    return redirect(url_for("inventory_list"))


# --------------------------------------------------------- customers (M7)
@app.route("/customers")
@login_required
def customers_list():
    db = get_db()
    rows = db.execute(
        "SELECT c.*, COUNT(o.id) AS total_orders, COALESCE(SUM(o.total_amount),0) AS total_spending "
        "FROM customers c LEFT JOIN orders o ON o.customer_id = c.id "
        "GROUP BY c.id ORDER BY total_spending DESC"
    ).fetchall()
    db.close()
    return render_template("customers.html", customers=rows)


@app.route("/customers/<int:customer_id>")
@login_required
def customer_detail(customer_id):
    db = get_db()
    customer = db.execute("SELECT * FROM customers WHERE id=?", (customer_id,)).fetchone()
    orders = db.execute(
        "SELECT * FROM orders WHERE customer_id=? ORDER BY id DESC", (customer_id,)
    ).fetchall()
    db.close()
    return render_template("customer_detail.html", customer=customer, orders=orders)


# ----------------------------------------------------------- reports (M9)
@app.route("/reports")
@login_required
def reports():
    db = get_db()
    daily = db.execute(
        "SELECT order_date, COUNT(*) AS orders, SUM(total_amount) AS revenue "
        "FROM orders GROUP BY order_date ORDER BY order_date DESC"
    ).fetchall()
    db.close()
    return render_template("reports.html", daily=daily)


@app.route("/reports/export.csv")
@login_required
def reports_export_csv():
    db = get_db()
    rows = db.execute(
        "SELECT order_date, COUNT(*) AS orders, SUM(total_amount) AS revenue "
        "FROM orders GROUP BY order_date ORDER BY order_date DESC"
    ).fetchall()
    db.close()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Date", "Orders", "Revenue"])
    for r in rows:
        writer.writerow([r["order_date"], r["orders"], r["revenue"]])
    buf.seek(0)
    mem = io.BytesIO(buf.getvalue().encode("utf-8"))
    return send_file(mem, mimetype="text/csv", as_attachment=True,
                      download_name="sales_report.csv")


# --------------------------------------------------- AI prediction (M10)
@app.route("/predict", methods=["GET", "POST"])
@login_required
def predict():
    result = None
    form_data = {}
    if request.method == "POST":
        form_data = request.form.to_dict()
        try:
            result = predict_demand(
                day=form_data["day"], weather=form_data["weather"],
                temperature=form_data["temperature"], festival=form_data["festival"],
                holiday=form_data["holiday"], time_slot=form_data["time_slot"],
            )
            db = get_db()
            db.execute(
                "INSERT INTO predictions (day, weather, temperature, festival, holiday, "
                "time_slot, predicted_orders, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (form_data["day"], form_data["weather"], form_data["temperature"],
                 form_data["festival"], form_data["holiday"], form_data["time_slot"],
                 result["predicted_orders"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )
            db.commit()
            db.close()
        except FileNotFoundError as e:
            flash(str(e), "danger")
    return render_template("predict.html", result=result, form_data=form_data)


if __name__ == "__main__":
    app.run(debug=True)
