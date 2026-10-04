"""
db.py - lightweight sqlite3 database layer (no ORM needed -> keeps the
project small and dependency-free). Provides get_db() and init_db().
"""
import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "canteen.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables (if missing) and seed demo data on first run."""
    first_run = not os.path.exists(DB_PATH)
    conn = get_db()
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    conn.commit()

    if first_run:
        seed(conn)
    conn.close()


def seed(conn):
    cur = conn.cursor()

    # default admin: username=admin password=admin123
    cur.execute(
        "INSERT INTO admin (username, password_hash, full_name) VALUES (?, ?, ?)",
        ("admin", generate_password_hash("admin123"), "Canteen Administrator"),
    )

    foods = [
        ("Veg Thali", "Meals", 60, 40, "Available"),
        ("Chicken Biryani", "Meals", 120, 25, "Available"),
        ("Masala Dosa", "South Indian", 45, 30, "Available"),
        ("Samosa", "Snacks", 15, 60, "Available"),
        ("Paneer Roll", "Snacks", 55, 20, "Available"),
        ("Cold Coffee", "Beverages", 40, 35, "Available"),
        ("Tea", "Beverages", 10, 100, "Available"),
        ("Sandwich", "Snacks", 35, 8, "Available"),
    ]
    cur.executemany(
        "INSERT INTO food (name, category, price, quantity, status) VALUES (?, ?, ?, ?, ?)",
        foods,
    )

    customers = [
        ("Rahul Sharma", "9876500001", "rahul@example.com"),
        ("Priya Verma", "9876500002", "priya@example.com"),
        ("Amit Singh", "9876500003", "amit@example.com"),
    ]
    cur.executemany(
        "INSERT INTO customers (name, phone, email) VALUES (?, ?, ?)", customers
    )

    inventory = [
        ("Rice", 25, "kg", 10),
        ("Paneer", 8, "kg", 5),
        ("Milk", 15, "litre", 8),
        ("Flour", 3, "kg", 5),  # intentionally low stock for demo
        ("Tea Powder", 2, "kg", 3),
    ]
    cur.executemany(
        "INSERT INTO inventory (ingredient_name, available_quantity, unit, minimum_stock) "
        "VALUES (?, ?, ?, ?)",
        inventory,
    )

    conn.commit()
