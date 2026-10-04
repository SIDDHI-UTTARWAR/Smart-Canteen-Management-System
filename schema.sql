-- Smart Canteen Management System - Database Schema (SQLite)
-- Run automatically by app.py on first launch (see init_db()).
-- MySQL note: this schema is 95% MySQL-compatible; just change
-- AUTOINCREMENT -> AUTO_INCREMENT and INTEGER PRIMARY KEY -> INT PRIMARY KEY.

CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT
);

CREATE TABLE IF NOT EXISTS food (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER DEFAULT 0,
    image TEXT DEFAULT 'default_food.png',
    status TEXT DEFAULT 'Available'
);

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT UNIQUE,
    email TEXT
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    order_time TEXT NOT NULL,
    total_amount REAL DEFAULT 0,
    status TEXT DEFAULT 'Completed',
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    food_id INTEGER NOT NULL,
    food_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price_each REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (food_id) REFERENCES food(id)
);

CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_name TEXT NOT NULL,
    available_quantity REAL DEFAULT 0,
    unit TEXT DEFAULT 'kg',
    minimum_stock REAL DEFAULT 5
);

CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL UNIQUE,
    subtotal REAL NOT NULL,
    gst_percent REAL DEFAULT 5,
    gst_amount REAL DEFAULT 0,
    discount_percent REAL DEFAULT 0,
    discount_amount REAL DEFAULT 0,
    final_total REAL NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day TEXT, weather TEXT, temperature REAL,
    festival TEXT, holiday TEXT, time_slot TEXT,
    predicted_orders REAL,
    created_at TEXT
);
