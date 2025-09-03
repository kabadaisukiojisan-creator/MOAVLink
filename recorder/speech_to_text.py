
import os
import io
import wave
import time
import json
import queue
import pyaudio
import keyboard
import threading
import configparser
import simpleaudio as sa
import speech_recognition as sr

from datetime import datetime

config = configparser.ConfigParser()
config.read("config/config.ini", encoding="utf-8")

GUI_LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs", "gui_log.json")
MIC_DEVICE_INDEX = int(config["RECORDER"]["mic_device_index"])
INPUTS_DIR = config["GENERAL"].get("inputs_dir", "outputs/inputs")
QUESTION_SUFFIXES = [
    suffix.strip() for suffix in config["CONVERSATION"]["question_suffixes"].split(",")
]
RECORD_KEY = config["KEYS"].get("record_key", "F9")

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
SPLIT_SEC = 3.0
TIME_OUT = 1


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

def play_sound(file_path):
    try:
        wave_obj = sa.WaveObject.from_wave_file(file_path)
        wave_obj.play()
    except Exception as e:
        print(f"[ERROR] 効果音再生失敗: {file_path} ({e})")

def is_question(text: str) -> bool:
    return any(text.strip().endswith(suffix) for suffix in QUESTION_SUFFIXES)

def record_audio():

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=MIC_DEVICE_INDEX,
                    frames_per_buffer=CHUNK)

    frames = []
    print("録音開始")

    # 非同期認識タスク用キュー
    partial_q = queue.Queue()

    def recognize_worker():
        recognizer = sr.Recognizer()
        while True:
            part = partial_q.get()
            if part is None:  # 終了シグナル
                break
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b"".join(part))
            wav_buffer.seek(0)
            try:
                with sr.AudioFile(wav_buffer) as source:
                    audio = recognizer.record(source)
                text = recognizer.recognize_google(audio, language="ja-JP")
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print(f"[ERROR] Google Speech API に接続できません: {e}")

    # 部分認識スレッド起動
    worker = threading.Thread(target=recognize_worker, daemon=True)
    worker.start()

    start_time = time.time()
    part_frames = []

    # F9押下中は録音継続しつつ、一定間隔ごとに部分認識（非同期）
    # 録音ループ
    while keyboard.is_pressed(RECORD_KEY):
        data = stream.read(CHUNK)
        frames.append(data)
        part_frames.append(data)

        # 3秒ごとに部分認識へ投入
        if time.time() - start_time >= SPLIT_SEC:
            partial_q.put(part_frames.copy())
            part_frames.clear()
            start_time = time.time()

    stream.stop_stream()
    stream.close()
    p.terminate()

    if not frames:
        play_sound("sounds/timeout.wav")
        print("【INFO】音声が取得できませんでした")
        partial_q.put(None)
        return None

    # 最後の残りを処理
    if part_frames:
        partial_q.put(part_frames.copy())

    # 全文をまとめて最終認識
    audio_data = b"".join(frames)
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(audio_data)

    wav_buffer.seek(0)
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_buffer) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio, language="ja-JP")
    except sr.UnknownValueError:
        text = ""
    except sr.RequestError as e:
        print(f"[ERROR] Google Speech API に接続できません: {e}")
        text = ""

    # 終了シグナルを送って worker を閉じる
    partial_q.put(None)
    worker.join(timeout=TIME_OUT)

    # 疑問符付与処理
    if text and is_question(text) and not text.endswith("？"):
        text = text + "？"
    
    # --- GUIログに逐次保存 ---
    append_gui_log("user", text)

    return text

def save_input_text(text):
    """認識結果をファイルに保存"""
    if text is None:
        return None

    date_dir = os.path.join(INPUTS_DIR, datetime.now().strftime("%Y%m%d"))
    os.makedirs(date_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(date_dir, f"record_{timestamp}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    return filename
