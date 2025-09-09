# app.py

# Before run change venv!!
# Remember to move to 記帳app
# terminal type: venv\Scripts\activate
# Then run: uvicorn app:app --reload

from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import joblib
from fastapi.middleware.cors import CORSMiddleware

import db_setup

# 初始化 FastAPI
app = FastAPI(
    docs_url="/",       # Swagger UI 直接在 /
    redoc_url=None,     # 可選：關掉 /redoc
    openapi_url="/openapi.json",
)

# CORS middleware（讓前端 HTML 可以呼叫 API）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開發時先允許全部
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 載入 ML 模型與向量器
clf = joblib.load("model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

# 定義交易輸入資料格式


class TransactionIn(BaseModel):
    date: str
    amount: float
    description: str


# 建立資料表（如果還沒建）
db_setup.init_db()

# 插入一筆交易


def insert_transaction(date, amount, description, category):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transactions (date, amount, description, category) VALUES (?, ?, ?, ?)",
        (date, amount, description, category)
    )
    conn.commit()
    conn.close()

# Root endpoint


@app.get("/")
def root():
    return {"message": "Hello, FastAPI is working!"}

# 新增交易


@app.post("/transactions")
def add_transaction(t: TransactionIn):
    # ML 預測類別
    X = vectorizer.transform([t.description])
    category = clf.predict(X)[0]

    # 存到 DB
    insert_transaction(t.date, t.amount, t.description, category)

    return {
        "date": t.date,
        "amount": t.amount,
        "description": t.description,
        "predicted_category": category
    }

# 回傳 summary (給 Chart.js 使用)


@app.get("/summary")
def get_summary():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT category, SUM(amount) FROM transactions GROUP BY category")
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}


@app.get("/transactions")
def get_transactions():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT date, amount, description, category FROM transactions ORDER BY date ASC")
    rows = cursor.fetchall()
    conn.close()

    # 格式化成 JSON
    transactions = [
        {"date": r[0], "amount": r[1], "description": r[2], "category": r[3]}
        for r in rows
    ]
    return transactions
