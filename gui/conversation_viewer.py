import tkinter as tk
import json
import os
import configparser
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

config = configparser.ConfigParser()
config.read("config/config.ini", encoding="utf-8")
LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs", "gui_log.json")
RECORD_KEY = config["KEYS"]["record_key"]
EXIT_KEY = config["KEYS"]["exit_key"]

# === 初回起動時、ログファイルがなければ空のJSONを作成 ===
if not os.path.exists(LOG_PATH):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

class LogHandler(FileSystemEventHandler):
    def __init__(self, text_area, status_label):
        self.text_area = text_area
        self.status_label = status_label

    def on_modified(self, event):
        if event.src_path.endswith("gui_log.json"):
            self.update_log()

    def update_log(self):
        try:
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return

        self.text_area.config(state="normal")
        self.text_area.delete("1.0", tk.END)

        if data:
            for turn in data[-15:]:  # 直近15件だけ表示
                if "user" in turn and turn["user"]:
                    self.text_area.insert(tk.END, f"入力 : {turn['user']}\n")
                if "assistant" in turn and turn["assistant"]:
                    self.text_area.insert(tk.END, f"応答 : {turn['assistant']}\n\n")
            self.status_label.config(text=f"直近 {len(data[-20:])} 件の会話を表示中")
        else:
            self.text_area.insert(tk.END, f"まだ会話は記録されていません。\n{RECORD_KEY.upper()}キーで録音開始、{EXIT_KEY.upper()}キーで終了\n")
            self.status_label.config(text="待機中...")

        self.text_area.config(state="disabled")

def show_conversation():
    root = tk.Tk()
    root.title("MOAVLink 会話ビューア")

    status_label = tk.Label(root, text="VOICEVOXエンジン起動完了！ / F9キーで録音開始、ESCキーで終了", anchor="w")
    status_label.pack(fill="x", padx=10, pady=5)

    text_area = tk.Text(root, wrap="word", width=80, height=30, font=("Meiryo", 11))
    text_area.pack(padx=10, pady=10)

    # 監視開始
    event_handler = LogHandler(text_area, status_label)
    observer = Observer()
    observer.schedule(event_handler, os.path.dirname(LOG_PATH), recursive=False)
    observer.start()

    # 初回ロード
    event_handler.update_log()

    root.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()
    observer.stop()
    observer.join()

if __name__ == "__main__":
    show_conversation()
