import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 當前檔案所在資料夾
db_path = os.path.join(BASE_DIR, "expenses.db")

conn = sqlite3.connect(db_path)

cursor = conn.cursor()

# Create Table

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    category TEXT
)
               """)

conn.commit()
conn.close()
print("Table being created and initialized")
