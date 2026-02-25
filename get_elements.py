import sqlite3

with sqlite3.connect("tracker.db") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products_diego")
    print(cursor.fetchall())
