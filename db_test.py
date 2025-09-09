import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 取得目前檔案所在的資料夾
db_path = os.path.join(BASE_DIR, "expenses.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

"""

Delete all row and reset auto increment

"""
cursor.execute(
    "DELETE FROM transactions;")
cursor.execute("DELETE FROM sqlite_sequence WHERE name='transactions';")

# Add stuff to it
# cursor.execute("INSERT INTO transactions (date, amount, description, category) VALUES (?,?,?,?)",
#                ("2025-09-07", 10.5, "Starbucks Coffee", "Food"))
conn.commit()

cursor.execute("SELECT * FROM transactions")
rows = cursor.fetchall()

for r in rows:
    print(r)

conn.close()
