
import csv
import sqlite3
from pathlib import Path

RAW = Path("data/raw")
PROCESSED = Path("data/processed")
PROCESSED.mkdir(parents=True, exist_ok=True)

DB = "restaurant.db"


def read_csv(filename):
    with open(RAW / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def run_etl():
    print("STEP 1: Extracting data...")

    menu = read_csv("menu.csv")
    orders = read_csv("orders.csv")
    items = read_csv("order_items.csv")

    print(f"Menu: {len(menu)}, Orders: {len(orders)}, Items: {len(items)}")

    print("STEP 2: Transforming data...")

    menu_map = {int(m["item_id"]): m for m in menu}
    order_map = {int(o["order_id"]): o for o in orders}

    clean_items = []
    rejected = 0

    for item in items:
        try:
            order_id = int(item["order_id"])
            item_id = int(item["item_id"])
            quantity = int(item["quantity"])

            if order_id not in order_map or item_id not in menu_map:
                rejected += 1
                continue

            if quantity <= 0:
                rejected += 1
                continue

            order = order_map[order_id]
            dish = menu_map[item_id]
            revenue = quantity * float(dish["price"])

            clean_items.append({
                "order_id": order_id,
                "order_date": order["order_date"],
                "status": order["status"],
                "order_type": order["order_type"],
                "payment_method": order["payment_method"],
                "item_id": item_id,
                "item_name": dish["item_name"],
                "category": dish["category"],
                "quantity": quantity,
                "unit_price": float(dish["price"]),
                "line_revenue": round(revenue, 2)
            })

        except (ValueError, KeyError):
            rejected += 1

    with open(
        PROCESSED / "clean_sales.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as f:
        fields = list(clean_items[0].keys()) if clean_items else []
        writer = csv.DictWriter(f, fieldnames=fields)
        if fields:
            writer.writeheader()
            writer.writerows(clean_items)

    print("STEP 3: Loading data into SQLite...")

    with sqlite3.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS menu (
                item_id INTEGER PRIMARY KEY,
                item_name TEXT,
                category TEXT,
                price REAL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY,
                order_date TEXT,
                order_type TEXT,
                payment_method TEXT,
                status TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                order_id INTEGER,
                item_id INTEGER,
                quantity INTEGER
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clean_sales (
                order_id INTEGER,
                order_date TEXT,
                status TEXT,
                order_type TEXT,
                payment_method TEXT,
                item_id INTEGER,
                item_name TEXT,
                category TEXT,
                quantity INTEGER,
                unit_price REAL,
                line_revenue REAL
            )
        """)

        conn.execute("DELETE FROM menu")
        conn.execute("DELETE FROM orders")
        conn.execute("DELETE FROM order_items")
        conn.execute("DELETE FROM clean_sales")

        conn.executemany(
            "INSERT INTO menu VALUES (?, ?, ?, ?)",
            [(int(m["item_id"]), m["item_name"],
              m["category"], float(m["price"])) for m in menu]
        )

        conn.executemany(
            "INSERT INTO orders VALUES (?, ?, ?, ?, ?)",
            [(int(o["order_id"]), o["order_date"],
              o["order_type"], o["payment_method"], o["status"])
             for o in orders]
        )

        conn.executemany(
            "INSERT INTO order_items VALUES (?, ?, ?)",
            [(int(i["order_id"]), int(i["item_id"]),
              int(i["quantity"])) for i in items]
        )

        conn.executemany("""
            INSERT INTO clean_sales VALUES (
                :order_id, :order_date, :status, :order_type,
                :payment_method, :item_id, :item_name, :category,
                :quantity, :unit_price, :line_revenue
            )
        """, clean_items)

    completed = sum(
        1 for row in clean_items if row["status"] == "Completed"
    )
    revenue = sum(
        row["line_revenue"] for row in clean_items
        if row["status"] == "Completed"
    )

    print("\nETL PIPELINE COMPLETED!")
    print("Clean sales rows:", len(clean_items))
    print("Rejected rows:", rejected)
    print("Completed order lines:", completed)
    print(f"Completed-order revenue: Rs. {revenue:.2f}")
    print("Database created:", DB)
    print("Processed CSV:", PROCESSED / "clean_sales.csv")


if __name__ == "__main__":
    run_etl()
