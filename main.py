import os
import sys
import time
import json
import random
import keyboard
import threading
import configparser

from main_method import start_engine, stop_engine, bring_console_to_front, init_gui_log, start_gui, stop_gui, handle_recording


config = configparser.ConfigParser()
config.read("config/config.ini", encoding="utf-8")

# speak処理のimport
engine = config.get("SPEECH_ENGINE", "engine", fallback="voicevox").lower()
if engine == "coeiroink":
    from voice.voicecoeiroink_client import speak
else:
    from voice.voicevox_client import speak

EXIT_KEY = config["KEYS"]["exit_key"]
RECORD_KEY = config["KEYS"]["record_key"]
END_MESSAGE = [m.strip() for m in config["GENERAL"].get("end_messages", "").split(",") if m.strip()]
STANDBY_MESSAGE = [m.strip() for m in config["GENERAL"].get("standby_messages", "").split(",") if m.strip()]

def main():
    # エンジン起動
    if not start_engine():
        return  # 起動失敗なら終了

    #ログ表示GUI起動
    init_gui_log()
    start_gui()

    print(f"{RECORD_KEY.upper()}キーで録音開始、{EXIT_KEY.upper()}キーで終了")
    if STANDBY_MESSAGE:
        message = random.choice(STANDBY_MESSAGE)
        speak(message)
        time.sleep(0.5)
    keyboard.add_hotkey(RECORD_KEY, lambda: threading.Thread(target=handle_recording).start())
    keyboard.wait(EXIT_KEY)
    if END_MESSAGE:
        message = random.choice(END_MESSAGE)
        speak(message)
    print("終了します")

    # VOICEVOXエンジンを終了
    stop_gui() 
    stop_engine()
    bring_console_to_front()

if __name__ == "__main__":
    try:
        main()
    finally:
        stop_engine()
        stop_gui() 
        sys.exit(0)
