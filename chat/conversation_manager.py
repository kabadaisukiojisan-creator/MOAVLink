import os
import json
from datetime import datetime, timedelta
import configparser
from openai import OpenAI

from memory.vector_store import init_db, save_conversation_to_db, search_similar

# -------------------------
# 設定読み込み
# -------------------------
config = configparser.ConfigParser()
config.read("config/config.ini", encoding="utf-8")

API_KEY = config["CHAT"]["api_key"]
MODEL = config["CHAT"].get("model", "gpt-4o-mini")
LONG_TERM_HITS = int(config["MEMORY"].get("long_term_hits", 5))  # 上位件数を設定で調整可能

CONVERSATION_LOG = "outputs/conversation_log.json"

client = OpenAI(api_key=API_KEY)

# DB 初期化
init_db()

# -------------------------
# 短期記憶
# -------------------------
def load_conversation_history(limit=5):
    """直近の会話を取得（短期記憶用）"""
    if not os.path.exists(CONVERSATION_LOG):
        return []

    with open(CONVERSATION_LOG, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data[-limit:]

# -------------------------
# 会話保存（JSON + ベクトルDB）
# -------------------------
def save_conversation(user_text, assistant_text):
    os.makedirs(os.path.dirname(CONVERSATION_LOG), exist_ok=True)

    log_entry_user = {
        "timestamp": datetime.now().isoformat(),
        "user": user_text,
        "assistant": assistant_text
    }

    # JSON保存
    if os.path.exists(CONVERSATION_LOG):
        with open(CONVERSATION_LOG, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(log_entry_user)
    with open(CONVERSATION_LOG, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # ベクトルDB保存
    save_conversation_to_db(datetime.now().isoformat(), "user", user_text)
    save_conversation_to_db(datetime.now().isoformat(), "assistant", assistant_text)

# -------------------------
# 中期記憶（要約）
# -------------------------
def load_summary(days=3):
    """過去N日分の要約を GPT で作成"""
    if not os.path.exists(CONVERSATION_LOG):
        return ""

    with open(CONVERSATION_LOG, "r", encoding="utf-8") as f:
        data = json.load(f)

    cutoff = datetime.now() - timedelta(days=days)
    recent = [entry for entry in data if datetime.fromisoformat(entry["timestamp"]) >= cutoff]

    if not recent:
        return "要約対象なし"

    conversation_text = "\n".join(
        [f"ユーザー: {e['user']} / 紗霧: {e['assistant']}" for e in recent]
    )

    # GPTで要約
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "あなたは親しみやすく感情豊かで自然な口調で会話を続けるれるAIです。話が途切れないよう、ユーザーの言葉に共感しつつ、関連する話題で返答してください。"},
            {"role": "user", "content": conversation_text}
        ]
    )
    return response.choices[0].message.content.strip()

# -------------------------
# 長期記憶（ベクトル検索）
# -------------------------
def search_long_term(query, min_score=0.5):
    """ベクトル検索で長期記憶を取得（スコア閾値あり）"""
    results = search_similar(query, top_n=LONG_TERM_HITS)
    hits = []
    for score, row in results:
        if score < min_score:
            continue
        hits.append({
            "timestamp": row[1],
            "role": row[2],
            "content": row[3],
            "score": float(score)  # JSON化できるようにfloatに変換
        })
    return hits
