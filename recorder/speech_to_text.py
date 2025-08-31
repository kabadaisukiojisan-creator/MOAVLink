
import speech_recognition as sr
from datetime import datetime
import os
import configparser
import simpleaudio as sa
import pyaudio
import wave
import keyboard

config = configparser.ConfigParser()
config.read("config/config.ini", encoding="utf-8")

MIC_DEVICE_INDEX = int(config["RECORDER"]["mic_device_index"])
INPUTS_DIR = config["GENERAL"].get("inputs_dir", "outputs/inputs")
QUESTION_SUFFIXES = [
    suffix.strip() for suffix in config["CONVERSATION"]["question_suffixes"].split(",")
]

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

def play_sound(file_path):
    try:
        wave_obj = sa.WaveObject.from_wave_file(file_path)
        wave_obj.play()
    except Exception as e:
        print(f"[ERROR] 効果音再生失敗: {file_path} ({e})")

def is_question(text: str) -> bool:
    return any(text.strip().endswith(suffix) for suffix in QUESTION_SUFFIXES)

def record_audio():
    """F9押下中だけ録音、離したら終了（非ブロッキング構成）"""
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=MIC_DEVICE_INDEX,
                    frames_per_buffer=CHUNK)

    frames = []
    print("録音開始")

    while keyboard.is_pressed("f9"):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    if not frames:
        play_sound("sounds/timeout.wav")
        print("【INFO】音声が取得できませんでした")
        return None

    # 一時的なWAVファイルへ保存
    os.makedirs("outputs/temp_audio", exist_ok=True)
    temp_path = os.path.join("outputs/temp_audio", "temp.wav")
    wf = wave.open(temp_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    recognizer = sr.Recognizer()
    with sr.AudioFile(temp_path) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio, language="ja-JP")
        if is_question(text):
            print("【INFO】疑問文の可能性が高い")
            if not text.strip().endswith("？"):
                text += "？"
        else:
            print("【INFO】疑問文ではなさそう")
        return text
    except sr.UnknownValueError:
        play_sound("sounds/timeout.wav")
        print("【INFO】音声を認識できませんでした")
    except sr.RequestError as e:
        print(f"[ERROR] 音声認識サービスに接続できません: {e}")
    return None

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
