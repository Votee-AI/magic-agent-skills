#!/usr/bin/env python3
"""Create the test SQLite database for database integration evals.

Run once to generate tests/fixtures/test_database.sqlite:
    python3 tests/fixtures/create_test_db.py

Tables:
    customers  — primary entity, various column types
    orders     — FK to customers, dates, amounts
    products   — standalone lookup table
    order_items — junction table: orders ↔ products (many-to-many)
"""

import sqlite3
import random
from pathlib import Path
from datetime import date, timedelta

DB_PATH = Path(__file__).parent / "test_database.sqlite"

REGIONS = ["North", "South", "East", "West", "Central"]
STATUSES = ["active", "inactive", "pending"]
CATEGORIES = ["Electronics", "Books", "Clothing", "Food", "Tools"]
PRODUCT_NAMES = [
    "Widget A", "Widget B", "Gadget X", "Gadget Y", "Gizmo Z",
    "Book: Python", "Book: SQL", "Book: Data", "Shirt M", "Shirt L",
    "Snack Pack", "Tool Kit", "Sensor V2", "Cable USB-C", "Adapter HDMI",
]


def create_tables(cur: sqlite3.Cursor) -> None:
    cur.executescript("""
        CREATE TABLE customers (
            id          INTEGER PRIMARY KEY,
            name        TEXT NOT NULL,
            email       TEXT UNIQUE NOT NULL,
            region      TEXT NOT NULL,
            age         INTEGER,
            income      REAL,
            is_active   INTEGER NOT NULL DEFAULT 1,
            notes       TEXT,
            created_at  TEXT NOT NULL
        );

        CREATE TABLE products (
            id          INTEGER PRIMARY KEY,
            name        TEXT NOT NULL,
            category    TEXT NOT NULL,
            price       REAL NOT NULL CHECK(price >= 0),
            in_stock    INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE orders (
            id           INTEGER PRIMARY KEY,
            customer_id  INTEGER NOT NULL,
            order_date   TEXT NOT NULL,
            total_amount REAL NOT NULL,
            status       TEXT NOT NULL DEFAULT 'pending',
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        );

        CREATE TABLE order_items (
            id          INTEGER PRIMARY KEY,
            order_id    INTEGER NOT NULL,
            product_id  INTEGER NOT NULL,
            quantity    INTEGER NOT NULL CHECK(quantity > 0),
            unit_price  REAL NOT NULL,
            FOREIGN KEY (order_id)   REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
    """)


def seed_data(cur: sqlite3.Cursor) -> None:
    random.seed(42)
    base_date = date(2024, 1, 1)

    # -- customers (50 rows, some with nulls) --
    sentinels = ["N/A", "TBD", None]
    for i in range(1, 51):
        age = random.randint(18, 75) if random.random() > 0.1 else None
        income = round(random.uniform(25000, 150000), 2) if random.random() > 0.15 else None
        notes = random.choice(sentinels) if random.random() > 0.6 else f"Customer note {i}"
        cur.execute(
            "INSERT INTO customers (id, name, email, region, age, income, is_active, notes, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (i, f"Customer {i}", f"customer{i}@example.com", random.choice(REGIONS),
             age, income, 1 if random.random() > 0.2 else 0, notes,
             (base_date + timedelta(days=random.randint(0, 365))).isoformat()),
        )

    # -- products (15 rows) --
    for i, name in enumerate(PRODUCT_NAMES, 1):
        cur.execute(
            "INSERT INTO products (id, name, category, price, in_stock) VALUES (?, ?, ?, ?, ?)",
            (i, name, random.choice(CATEGORIES),
             round(random.uniform(5.0, 500.0), 2), 1 if random.random() > 0.1 else 0),
        )

    # -- orders (120 rows) --
    for i in range(1, 121):
        cust_id = random.randint(1, 50)
        order_date = (base_date + timedelta(days=random.randint(0, 500))).isoformat()
        total = round(random.uniform(10, 2000), 2)
        status = random.choice(["completed", "completed", "pending", "cancelled"])
        cur.execute(
            "INSERT INTO orders (id, customer_id, order_date, total_amount, status) VALUES (?, ?, ?, ?, ?)",
            (i, cust_id, order_date, total, status),
        )

    # -- order_items (250 rows) --
    item_id = 1
    for order_id in range(1, 121):
        n_items = random.randint(1, 4)
        used_products = random.sample(range(1, 16), min(n_items, 15))
        for prod_id in used_products:
            qty = random.randint(1, 5)
            price = round(random.uniform(5.0, 500.0), 2)
            cur.execute(
                "INSERT INTO order_items (id, order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?, ?)",
                (item_id, order_id, prod_id, qty, price),
            )
            item_id += 1


def main() -> None:
    DB_PATH.unlink(missing_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    create_tables(cur)
    seed_data(cur)
    conn.commit()

    # Verify
    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"Created {DB_PATH}")
    for (t,) in tables:
        count = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t}: {count} rows")
    conn.close()


if __name__ == "__main__":
    main()
