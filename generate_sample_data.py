
import csv
import random
from pathlib import Path
from datetime import date, timedelta

random.seed(42)

raw = Path("data/raw")
raw.mkdir(parents=True, exist_ok=True)

menu = [
    [1, "Veg Burger", "Fast Food", 99],
    [2, "Cheese Pizza", "Pizza", 249],
    [3, "Margherita Pizza", "Pizza", 199],
    [4, "Paneer Tikka", "Starters", 229],
    [5, "French Fries", "Sides", 89],
    [6, "Veg Sandwich", "Fast Food", 119],
    [7, "White Sauce Pasta", "Pasta", 219],
    [8, "Masala Dosa", "South Indian", 129],
    [9, "Paneer Biryani", "Main Course", 239],
    [10, "Cold Coffee", "Beverages", 109],
    [11, "Chocolate Brownie", "Desserts", 99],
    [12, "Lemon Soda", "Beverages", 59],
]

def save_csv(filename, headers, rows):
    with open(raw / filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

save_csv("menu.csv", ["item_id", "item_name", "category", "price"], menu)

orders = []
items = []
start = date(2026, 9, 1)

for order_id in range(1001, 1061):
    order_date = start + timedelta(days=random.randint(0, 44))
    status = random.choices(
        ["Completed", "Cancelled"],
        weights=[85, 15]
    )[0]

    orders.append([
        order_id,
        order_date.isoformat(),
        random.choice(["Dine-in", "Takeaway", "Delivery"]),
        random.choice(["UPI", "Cash", "Card"]),
        status
    ])

    for item_id in random.sample(
        [m[0] for m in menu], random.randint(1, 4)
    ):
        items.append([
            order_id,
            item_id,
            random.randint(1, 3)
        ])

save_csv(
    "orders.csv",
    ["order_id", "order_date", "order_type", "payment_method", "status"],
    orders
)

save_csv(
    "order_items.csv",
    ["order_id", "item_id", "quantity"],
    items
)

print("SUCCESS: Restaurant sample data created!")
print("Menu items:", len(menu))
print("Orders:", len(orders))
print("Order item records:", len(items))
print("Files saved inside data/raw/")
