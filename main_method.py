# main_method.py
import os
import subprocess
import time
import ctypes
import shutil
import json
import requests
import configparser
import simpleaudio as sa

from recorder.speech_to_text import record_audio
from chat.gpt_client import get_response, save_response, stream_response

config = configparser.ConfigParser()
config.read("config/config.ini", encoding="utf-8")

GUI_LOG_PATH = os.path.join("outputs", "gui_log.json")
USE_STREAMING = config["CHAT"].getboolean("streaming", fallback=False)


# speak処理のimport
ENGINE = config.get("SPEECH_ENGINE", "engine", fallback="voicevox").lower()
if ENGINE == "coeiroink":
    from voice.voicecoeiroink_client import speak
elif ENGINE == "aivis":
    from voice.aivis_client import speak
else:
    from voice.voicevox_client import speak

# ==============================
# VOICEVOXエンジン制御
# ==============================
process = None
VOICEVOX_PATH = None

if ENGINE == "voicevox":
    VOICEVOX_PATH = config.get("VOICEVOXENGINE", "windows_directml", fallback="").strip()
    HOST = config["VOICEVOX"].get("host", "127.0.0.1")
    PORT = config["VOICEVOX"].get("port", "50021")
    if not VOICEVOX_PATH or not os.path.isfile(VOICEVOX_PATH):
        raise FileNotFoundError(f"VOICEVOXエンジンの実行ファイルが見つかりません: {VOICEVOX_PATH}")

COEIROINK_PATH = None
if ENGINE == "coeiroink":
    COEIROINK_PATH = config.get("COEIROINKENGINE", "coeiroink_directml", fallback="").strip()
    HOST = config["COEIROINK"].get("host", "127.0.0.1")
    PORT = config["COEIROINK"].get("port", "50032")
    if not COEIROINK_PATH or not os.path.isfile(COEIROINK_PATH):
        raise FileNotFoundError(f"COEIROINKエンジンの実行ファイルが見つかりません: {COEIROINK_PATH}")

AIVIS_PATH = None
if ENGINE == "aivis":
    AIVIS_PATH = config.get("AIVISENGINE", "aivis_directml", fallback="").strip()
    HOST = config["AIVIS"].get("host", "127.0.0.1")
    PORT = config["AIVIS"].get("port", "10101")
    GPU_MODE = config["AIVIS"].get("gpu", "n")
    if not AIVIS_PATH or not os.path.isfile(AIVIS_PATH):
        raise FileNotFoundError(f"AIVISENGINEエンジンの実行ファイルが見つかりません: {AIVIS_PATH}")

DOCS_URL = f"http://{HOST}:{PORT}/docs"

gui_process = None
is_processing = False  # 録音〜再生中ガード
engine_process = None


def start_engine():
    exe_path = None
    if ENGINE == "voicevox":
        return start_generic_engine(VOICEVOX_PATH)
    elif ENGINE == "coeiroink":
        return start_generic_engine(COEIROINK_PATH)
    elif ENGINE == "aivis":
        return start_aivis_engine()

def start_generic_engine(path):
    global engine_process
    print(f"エンジン起動中... ({path})")
    engine_process = subprocess.Popen([path])
    
    for _ in range(30):  # 最大30回（30秒）
        try:
            res = requests.get(DOCS_URL)
            if res.status_code == 200:
                print("エンジン起動完了！")
                return True
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError("エンジンが起動しませんでした。")
    print("エンジン起動完了！")
    return True

def start_aivis_engine():

    global engine_process
    engine_process = aivis_engine()
        
    for _ in range(30):  # 最大30回（30秒）
        try:
            res = requests.get(DOCS_URL)
            if res.status_code == 200:
                print("Aivisエンジン起動完了！")
                return True
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError("Aivisエンジンが起動しませんでした。")

def aivis_engine():
    if GPU_MODE == "y":
        return subprocess.Popen(["py", "-3.11", AIVIS_PATH, "--use_gpu"])
    else:
        return subprocess.Popen(["py", "-3.11", AIVIS_PATH])


def stop_engine():
    global engine_process
    if engine_process:
        print("エンジンを終了します...")
        engine_process.terminate()
        try:
            engine_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            engine_process.kill()
        engine_process = None
        print("エンジンを終了しました。")


def bring_console_to_front():
    """PowerShell（実行中のコンソール）を前面に戻す"""
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    user32 = ctypes.WinDLL('user32', use_last_error=True)

    hWnd = kernel32.GetConsoleWindow()
    if hWnd:
        user32.ShowWindow(hWnd, 9)
        user32.SetForegroundWindow(hWnd)


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


