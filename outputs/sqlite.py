import os
import sqlite3
import sys

# 引数チェック
if len(sys.argv) < 3:
    print("検索の文字列を出してください")
    sys.exit(1)

base_dir = sys.argv[1]
query = sys.argv[2]  # ← 第二引数を検索ワードとして利用

# DB ファイルのパス
DB_PATH = os.path.join(base_dir, "vector_store.db")

if not os.path.exists(DB_PATH):
    print(f"[ERROR] DBファイルが見つかりません: {DB_PATH}")
    sys.exit(1)

# DB の件数確認
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

count = c.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
print(f"DBに保存されている会話数: {count}")

# 検索処理
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
