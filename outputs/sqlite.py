#
#DB確認用pyDB内に現在何が登録されているか、また、検索した時何にがヒットするかを確認するよう
#
import sys, os
import sqlite3
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from chat.conversation_manager import search_long_term

DB_PATH = os.path.join("outputs", "vector_store.db")

# DBの件数確認
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
count = c.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
conn.close()
print(f"DBに保存されている会話数: {count}")

# 「夏」で検索
query = "動作"
results = search_long_term(query, min_score=0.3)

print(f"\n検索クエリ: {query}")
if results:
    for r in results:
        print(f"- [{r['role']}] {r['content']} (score={r['score']:.3f})")
else:
    print("→ 関連する記録は見つかりませんでした")