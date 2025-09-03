from openai import OpenAI
from datetime import datetime
import os
import configparser
import json
from memory.vector_store import save_conversation_to_db  # 先保存用（重複はvector側で除去）

from chat.conversation_manager import (
    load_conversation_history,
    save_conversation,
    load_summary,
    search_long_term
)

config = configparser.ConfigParser()
config.read("config/config.ini", encoding="utf-8")

# 必須セクション確認
REQUIRED_SECTIONS = ["GENERAL", "CHAT", "VOICEVOX", "MEMORY"]
for section in REQUIRED_SECTIONS:
    if section not in config:
        raise RuntimeError(f"app.config に {section} セクションがありません！")

RESPONSES_DIR = config["GENERAL"]["responses_dir"]
CHARACTER_PROMPT_FILE = config["CHAT"]["character_prompt_file"]
MODEL = config["CHAT"].get("model", "gpt-4o-mini")
API_KEY = config["CHAT"]["api_key"]
LONG_TERM_HITS = int(config["MEMORY"].get("long_term_hits",5))
MID_TERM_DAYS = int(config["MEMORY"].get("mid_term_days", 3))
LONG_TERM_MIN_SCORE = float(config["MEMORY"].get("long_term_min_score", 0.5))

CONVERSATION_LOG = "outputs/conversation_log.json"
GUI_LOG_PATH = os.path.join("outputs", "gui_log.json")
client = OpenAI(api_key=API_KEY)


def load_character_prompt():
    with open(CHARACTER_PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()

def append_gui_log(role, content):
    log_entry = {}
    if role == "user":
        log_entry["user"] = content
    elif role == "assistant":
        log_entry["assistant"] = content
    log_entry["timestamp"] = datetime.now().isoformat()

    try:
        if not os.path.exists(GUI_LOG_PATH):
            with open(GUI_LOG_PATH, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

        with open(GUI_LOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        data.append(log_entry)

        with open(GUI_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("GUIログ保存失敗:", e)

def save_memory_log(category, data):
    base_dir = os.path.join("outputs", "memory_logs")
    os.makedirs(base_dir, exist_ok=True)
    filename = os.path.join(base_dir, f"{category}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filename

def get_response(user_input):
    save_conversation_to_db(datetime.now().isoformat(), "user", user_input)
    prompt = load_character_prompt()
    messages = [{"role": "system", "content": prompt}]

    try:
        level = int(config["MEMORY"]["memory_level"])
    except Exception as e:
        raise RuntimeError("app.config の [MEMORY] セクションに正しい memory_level が設定されていません") from e

    # 短期記憶
    short_history = load_conversation_history(limit=LONG_TERM_HITS)
    for h in short_history:
        messages.append({"role": "user", "content": h["user"]})
        messages.append({"role": "assistant", "content": h["assistant"]})
    save_memory_log("short_term", short_history)

    # 中期記憶
    summary = ""
    if level >= 2:
        summary = load_summary(days=MID_TERM_DAYS)
        if summary:
            messages.append({"role": "system", "content": f"過去\n{mid_term_days}日分の要約:\n{summary}"})
    save_memory_log("mid_term", {"summary": summary})

    # 長期記憶（検索のみ、保存はlevel=3）
    hits = []
    long_term_data = {}

    if level >= 3:
        hits = search_long_term(user_input, min_score=LONG_TERM_MIN_SCORE)
        long_term_data = {
            "status": f"{len(hits)}件ヒット" if hits else "関連する記録は見つかりませんでした",
            "results": hits
        }
        save_memory_log("long_term", long_term_data)
    else:
        long_term_data = {"status": "long_term logging disabled at this memory level", "results": []}

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=1000,
        temperature=0.9,  # 出力にバリエーションをもたせる
        top_p=0.95        # 多様性を最大限許容
    )
    response_text = response.choices[0].message.content.strip()

    save_conversation(user_input, response_text)

    return response_text

# --- ストリーミング応答 ---
def stream_response(user_input):

    # ====== プロンプト & 記憶ロード ======
    prompt = load_character_prompt()
    messages = [{"role": "system", "content": prompt}]

    try:
        level = int(config["MEMORY"]["memory_level"])
    except Exception as e:
        raise RuntimeError("config.ini の [MEMORY] に正しい memory_level がありません") from e

    # --- 短期記憶 ---
    short_history = load_conversation_history(limit=LONG_TERM_HITS)
    for h in short_history:
        messages.append({"role": "user", "content": h["user"]})
        messages.append({"role": "assistant", "content": h["assistant"]})
    save_memory_log("short_term", short_history)

    # --- 中期記憶 ---
    summary = ""
    if level >= 2:
        summary = load_summary(days=MID_TERM_DAYS)
        if summary:
            messages.append({"role": "system", "content": f"過去{MID_TERM_DAYS}日分の要約:\n{summary}"})
    save_memory_log("mid_term", {"summary": summary})

    # --- 長期記憶 ---
    hits = []
    if level >= 3:
        hits = search_long_term(user_input, min_score=LONG_TERM_MIN_SCORE)
        if hits:
            messages.append({"role": "system", "content": f"長期記憶からの検索結果:\n{hits}"})
    save_memory_log("long_term", hits)

    # --- ユーザ入力 ---
    messages.append({"role": "user", "content": user_input})

    # ====== OpenAI ストリーミング応答 ======
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=True
    )

    buffer = ""
    full_text = ""
    # ストリーミング応答を文ごとに区切るためのデリミタ
    DELIMS = ["、", "。", "！", "？", "!", "?", "♪"]

    for chunk in response:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            buffer += delta.content
            if any(buffer.strip().endswith(d) for d in DELIMS) or len(buffer.strip()) > 40:
                seg = buffer.strip()
                # --- GUIログに逐次保存 ---
                append_gui_log("assistant", seg)
                yield seg
                full_text += seg
                buffer = ""

    if buffer.strip():
        append_gui_log("assistant", seg)
        yield buffer
        full_text += buffer
        


    # ====== 会話保存 ======
    save_conversation(user_input, full_text)

def save_response(text):
    date_dir = os.path.join(RESPONSES_DIR, datetime.now().strftime("%Y%m%d"))
    os.makedirs(date_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(date_dir, f"response_{timestamp}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    return filename
