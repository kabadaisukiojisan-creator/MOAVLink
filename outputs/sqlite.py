import os
import sqlite3

# DB ファイルのパス
DB_PATH = os.path.join("outputs", "vector_store.db")

# DB の件数確認
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
count = c.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
print(f"DBに保存されている会話数: {count}")

# 検索テスト（content列をLIKEで検索）
query = "夏"
results = c.execute(
    "SELECT role, content FROM conversations WHERE content LIKE ? LIMIT 10",
    (f"%{query}%",)
).fetchall()

conn.close()

print(f"\n検索クエリ: {query}")
if results:
    for role, content in results:
        print(f"- [{role}] {content}")
else:
    print("→ 関連する記録は見つかりませんでした")