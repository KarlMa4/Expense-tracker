# app.py
# ------------------------------------------------------------
# Before running:
#   Windows: venv\Scripts\activate
#   Mac:     source venv/bin/activate
# Then run:  uvicorn app:app --reload
# ------------------------------------------------------------

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import joblib

import db_setup

# ============================================================
# FastAPI Initialization
# ============================================================
app = FastAPI(
    docs_url="/",         # Swagger UI 直接在 /
    redoc_url=None,       # 關掉 /redoc
    openapi_url="/openapi.json",
)

# Enable CORS (for frontend HTML/JS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 開發時允許全部，之後可改成指定 domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Load ML Models
# ============================================================
clf = joblib.load("model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

# ============================================================
# Database Setup
# ============================================================
db_setup.init_db()

DB_PATH = "expenses.db"

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def insert_transaction(date: str, amount: float, description: str, category: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO transactions (date, amount, description, category)
        VALUES (?, ?, ?, ?)
        """,
        (date, amount, description, category)
    )
    conn.commit()
    conn.close()

# ============================================================
# Pydantic Models
# ============================================================
class TransactionIn(BaseModel):
    date: str
    amount: float
    description: str

class TransactionUpdate(BaseModel):
    category: str | None = None

# ============================================================
# Routes
# ============================================================

# Root
@app.get("/")
def root():
    return {"message": "Hello, FastAPI is working!"}


# Add Transaction
@app.post("/transactions")
def add_transaction(t: TransactionIn):
    try:
        # Predict category using ML
        X = vectorizer.transform([t.description])
        category = clf.predict(X)[0]

        # Save to DB
        insert_transaction(t.date, t.amount, t.description, category)

        return {
            "date": t.date,
            "amount": t.amount,
            "description": t.description,
            "predicted_category": category
        }
    except Exception as e:
        print("Error in /transactions:", e)
        return {"error": str(e)}


# Get All Transactions
@app.get("/transactions")
def get_transactions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, date, amount, description, category FROM transactions ORDER BY date ASC"
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {"id": r[0], "date": r[1], "amount": r[2], "description": r[3], "category": r[4]}
        for r in rows
    ]


# Update Transaction
@app.patch("/transactions/{tx_id}")
def update_transaction(tx_id: int, update: TransactionUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if exists
    cursor.execute("SELECT id FROM transactions WHERE id = ?", (tx_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Apply update
    if update.category:
        cursor.execute(
            "UPDATE transactions SET category = ? WHERE id = ?",
            (update.category, tx_id),
        )

    conn.commit()
    conn.close()
    return {"message": "Transaction updated successfully", "id": tx_id}


# Summary for charts
@app.get("/summary")
def get_summary():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT category, SUM(amount) FROM transactions GROUP BY category"
    )
    rows = cursor.fetchall()
    conn.close()

    return {row[0]: row[1] for row in rows}


# List ML categories
@app.get("/categories")
def get_categories():
    try:
        return {"categories": clf.classes_.tolist()}
    except Exception as e:
        return {"error": str(e)}
