import sqlite3
import numpy as np
from openai import OpenAI
from datetime import datetime, timedelta
import os
import configparser

# -------------------------
# 設定読み込み
# -------------------------
config = configparser.ConfigParser()
config.read("config/config.ini", encoding="utf-8")

API_KEY = config["CHAT"]["api_key"]
DB_PATH = os.path.join("outputs", "vector_store.db")

client = OpenAI(api_key=API_KEY)

# -------------------------
# DB 初期化
# -------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            role TEXT,
            content TEXT,
            embedding BLOB
        )
    """)
    conn.commit()
    conn.close()

# -------------------------
# Embedding 生成
# -------------------------
def create_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

# -------------------------
# 会話を保存（重複チェック付き）
# -------------------------
def save_conversation_to_db(timestamp, role, content, dedup_minutes=60):
    """会話を保存する（直近 dedup_minutes 分以内の重複は保存しない）"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 直近の同一発話チェック
    cutoff = (datetime.now() - timedelta(minutes=dedup_minutes)).isoformat()
    c.execute("""
        SELECT COUNT(*) FROM conversations
        WHERE role=? AND content=? AND timestamp > ?
    """, (role, content, cutoff))
    if c.fetchone()[0] > 0:
        conn.close()
        return  # 重複は保存しない

    # 保存
    embedding = create_embedding(content).tobytes()
    c.execute(
        "INSERT INTO conversations (timestamp, role, content, embedding) VALUES (?, ?, ?, ?)",
        (timestamp, role, content, embedding)
    )
    conn.commit()
    conn.close()

# -------------------------
# 類似検索（ユニーク化付き）
# -------------------------
def search_similar(text, top_n=5):
    query_vec = create_embedding(text)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, timestamp, role, content, embedding FROM conversations")
    rows = c.fetchall()
    conn.close()

    scored = []
    for row in rows:
        emb = np.frombuffer(row[4], dtype=np.float32)
        score = np.dot(query_vec, emb) / (np.linalg.norm(query_vec) * np.linalg.norm(emb))
        scored.append((score, row))

    scored.sort(key=lambda x: x[0], reverse=True)

    # content でユニーク化
    unique_results = {}
    for score, row in scored:
        if row[3] not in unique_results:
            unique_results[row[3]] = (score, row)

    return list(unique_results.values())[:top_n]
