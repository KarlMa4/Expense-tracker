import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 當前檔案所在資料夾
db_path = os.path.join(BASE_DIR, "expenses.db")


def init_db():
    """建立資料表（如果還沒建的話）"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

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
    print("✅ Database initialized (table ensured).")
