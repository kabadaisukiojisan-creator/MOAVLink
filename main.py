import os
import sys
import time
import json
import shutil
import random
import ctypes
import keyboard
import threading
import subprocess
import configparser
import simpleaudio as sa
import signal, subprocess

from voice.voicevox_client import speak
from recorder.speech_to_text import record_audio
from chat.gpt_client import get_response, save_response, stream_response

config = configparser.ConfigParser()
config.read("config/config.ini", encoding="utf-8")

EXIT_KEY = config["KEYS"]["exit_key"]
RECORD_KEY = config["KEYS"]["record_key"]
END_MESSAGE = [m.strip() for m in config["GENERAL"].get("end_messages", "").split(",") if m.strip()]
GUI_LOG_PATH = os.path.join("outputs", "gui_log.json")
USE_STREAMING = config["CHAT"].getboolean("streaming", fallback=False)
STANDBY_MESSAGE = [m.strip() for m in config["GENERAL"].get("standby_messages", "").split(",") if m.strip()]

VOICEVOX_PATH = config.get("VOICEVOXENGINE", "windows_directml", fallback="").strip()
if not VOICEVOX_PATH or not os.path.isfile(VOICEVOX_PATH):
    raise FileNotFoundError(f"VOICEVOXエンジンの実行ファイルが見つかりません: {VOICEVOX_PATH}")

gui_process = None
is_processing = False  # 録音〜再生中ガード
voicevox_process = None

def init_gui_log():
    with open(GUI_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

def start_gui():
    global gui_process
    gui_path = os.path.join(os.path.dirname(__file__), "gui", "conversation_viewer.py")
    gui_process = subprocess.Popen(["py", "-3.11", gui_path])

def stop_gui():
    global gui_process
    if gui_process and gui_process.poll() is None:
        try:
            gui_process.terminate()
            gui_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            gui_process.kill()
        except Exception as e:
            print(f"GUI終了時にエラー: {e}")
        finally:
            gui_process = None
        print("GUIを終了しました。")

def start_voicevox_engine():
    global voicevox_process
    config = configparser.ConfigParser()
    exe_path = VOICEVOX_PATH
    if not exe_path:
        print("VOICEVOXエンジンのパスが設定されていません。")
        return False

    print(f"VOICEVOXエンジン起動中... ({exe_path})")
    voicevox_process = subprocess.Popen([exe_path])
    time.sleep(5)
    print("VOICEVOXエンジン起動完了！")
    return True

def bring_console_to_front():
    """PowerShell（実行中のコンソール）を前面に戻す"""
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    user32 = ctypes.WinDLL('user32', use_last_error=True)

    hWnd = kernel32.GetConsoleWindow()
    if hWnd:
        user32.ShowWindow(hWnd, 9)
        user32.SetForegroundWindow(hWnd)

def stop_voicevox_engine():
    global voicevox_process
    if voicevox_process:
        print("VOICEVOXエンジンを終了します...")
        try:
            voicevox_process.terminate()
            time.sleep(2)
            if voicevox_process.poll() is None:
                voicevox_process.kill()  # まだ残ってたら強制終了
        except Exception as e:
            print(f"VOICEVOX終了時にエラー: {e}")
        finally:
            voicevox_process = None
        print("VOICEVOXエンジンを終了しました。")

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
        play_sound("sounds/beep.wav")  # ビープのみ再生
        user_text = record_audio()
        if user_text:
            print("入力:", user_text)
            if USE_STREAMING:
                print("返答（ストリーミング）:")
                full_reply = ""
                for segment in stream_response(user_text):
                    print(segment, end="", flush=True)
                    speak(segment)
                    full_reply += segment
                print()
                save_response(full_reply)
            else:
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
    #ボイスボ起動
    if not start_voicevox_engine():
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
    stop_voicevox_engine()
    bring_console_to_front()

if __name__ == "__main__":
    try:
        main()
    finally:
        stop_voicevox_engine()
        stop_gui() 
        sys.exit(0)
