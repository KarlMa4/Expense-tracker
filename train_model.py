import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 當前檔案所在資料夾

# 載入 Kaggle dataset
df = pd.read_csv(os.path.join(BASE_DIR, "data/Transactions.csv"))

# 檢查資料狀態
print("原始資料筆數：", len(df))
print("NaN 檢查：")
print(df.isna().sum())

# 清理資料：去掉 Note 或 Subcategory 缺失的列
df = df.dropna(subset=["Category", "Subcategory"])
# 確保是字串
df["Category"] = df["Category"].astype(str)
df["Subcategory"] = df["Subcategory"].astype(str)

print("清理後資料筆數：", len(df))

# 特徵與標籤
X = df["Subcategory"]
y = df["Category"]

# 向量化
vectorizer = TfidfVectorizer(max_features=5000)
X_vec = vectorizer.fit_transform(X)

# 模型訓練
clf = LogisticRegression(max_iter=500)
clf.fit(X_vec, y)

# 存檔
joblib.dump(clf, os.path.join(BASE_DIR, "model.pkl"))
joblib.dump(vectorizer, os.path.join(BASE_DIR, "vectorizer.pkl"))

print("✅ 模型訓練完成，類別：", clf.classes_)
