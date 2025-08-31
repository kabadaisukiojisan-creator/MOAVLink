import os
import time
import threading
import keyboard
import configparser
import shutil
import simpleaudio as sa
import random
from recorder.speech_to_text import record_audio
from chat.gpt_client import get_response, save_response
from voice.voicevox_client import speak


config = configparser.ConfigParser()
config.read("config/config.ini", encoding="utf-8")

RECORD_KEY = config["KEYS"]["record_key"]
EXIT_KEY = config["KEYS"]["exit_key"]
STANDBY_MESSAGE = [m.strip() for m in config["GENERAL"].get("standby_messages", "").split(",") if m.strip()]
END_MESSAGE = [m.strip() for m in config["GENERAL"].get("end_messages", "").split(",") if m.strip()]

is_processing = False  # 録音〜再生中ガード

def play_sound(file_path):
    try:
        wave_obj = sa.WaveObject.from_wave_file(file_path)
        wave_obj.play()
    except Exception as e:
        print(f"[ERROR] 効果音再生失敗: {file_path} ({e})")

def cleanup_response_and_record_dirs():
    base_dirs = [
        os.path.join("outputs", "records"),
        os.path.join("outputs", "responses"),
    ]

    for parent_dir in base_dirs:
        if os.path.exists(parent_dir):
            for folder in os.listdir(parent_dir):
                folder_path = os.path.join(parent_dir, folder)
                if os.path.isdir(folder_path):
                    try:
                        shutil.rmtree(folder_path)
                    except Exception as e:
                        print(f"[ERROR] 削除失敗: {folder_path} ({e})")

def handle_recording():
    global is_processing
    if is_processing:
        return
    is_processing = True
    try:
        play_sound("sounds/beep.wav")  # ビープのみ再生、メッセージ表示は record_audio 側で統一
        user_text = record_audio()
        if user_text:
            print("入力:", user_text)
            response = get_response(user_text)
            print("返答:", response)
            save_response(response)
            speak(response)
            cleanup_response_and_record_dirs()
    except Exception as e:
        print(f"[ERROR] 録音処理エラー: {e}")
    finally:
        is_processing = False

def main():
    print(f"{RECORD_KEY.upper()}キーで録音開始、{EXIT_KEY.upper()}キーで終了")
    if STANDBY_MESSAGE:
        message = random.choice(STANDBY_MESSAGE)
        speak(message)
        time.sleep(1)
    keyboard.add_hotkey(RECORD_KEY, lambda: threading.Thread(target=handle_recording).start())
    keyboard.wait(EXIT_KEY)
    if END_MESSAGE:
        message = random.choice(END_MESSAGE)
        speak(message)
        time.sleep(1)
    print("終了します")

if __name__ == "__main__":
    main()
