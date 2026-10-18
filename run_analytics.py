
import sqlite3
from pathlib import Path

DB = Path("restaurant.db")
SQL_FILE = Path("analytics.sql")

if not DB.exists():
    raise FileNotFoundError("Database missing. Run python3 etl.py first.")

if not SQL_FILE.exists():
    raise FileNotFoundError("analytics.sql file not found.")

sql_text = SQL_FILE.read_text(encoding="utf-8")

with sqlite3.connect(DB) as conn:
    statements = [
        s.strip() for s in sql_text.split(";") if s.strip()
    ]

    for number, statement in enumerate(statements, start=1):
        print(f"\n{'=' * 55}")
        print(f"QUERY {number}")
        print("=" * 55)

        cursor = conn.execute(statement)

        if cursor.description:
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            print(" | ".join(columns))
            print("-" * 55)

            for row in rows:
                print(" | ".join(str(value) for value in row))

            if not rows:
                print("No results found.")
        else:
            print("Query executed successfully.")

print("\nAll analytics queries completed!")
