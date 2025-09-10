import requests
import tempfile
import configparser
import os
import sounddevice as sd
import soundfile as sf
import time



# =========================
# 設定
# =========================
_config = configparser.ConfigParser()
_config.read("config/config.ini", encoding="utf-8")
_session = requests.Session()

ENGINE_MODE = _config["AIVIS"]["mode"]
AIVIS_API_KEY = _config["AIVIS"].get("api_key", "aivis_")
AIVIS_URL = _config["AIVIS"].get("url", "https://api.aivis-project.com/v1/tts/synthesize")
MODEL_UUID = _config["AIVIS"].get("model_uuid", "")
SPEAKER_ID = _config["AIVIS"].get("speaker_id", "")
USE_SSML = _config["AIVIS"].getboolean("use_ssml", True)
OUTPUT_FORMAT = _config["AIVIS"].get("output_format", "mp3")

AIVIS_HOST = _config["AIVIS"]["host"]
AIVIS_PORT = _config["AIVIS"]["port"]
AIVIS_LOCAL_URL = f"http://{AIVIS_HOST}:{AIVIS_PORT}"


def clean_audio_query(query: dict) -> dict:
    keys_to_remove = ["kana", "pauseLength"]
    return {k: v for k, v in query.items() if k not in keys_to_remove}

def tts_to_wav(text: str) -> str:
    start_time = time.time()
    print(f"[計測] OpenAIテキスト受信 → Aivis送信開始: {start_time:.3f}")
    print("通過1")
    headers = {
        "Authorization": f"Bearer {AIVIS_API_KEY}",
        "Content-Type": "application/json"
    }
    print("通過2")

    payload = {
        "model_uuid": MODEL_UUID,
        "text": text,
        "use_ssml": USE_SSML,
        "output_format": OUTPUT_FORMAT
    }
    print("通過3")

    response = requests.post(AIVIS_URL, headers=headers, json=payload)
    print(f"response:{response}")
    print("通過4")
        
    if response.status_code != 200:
        raise RuntimeError(f"Aivis TTS API Error: {response.status_code} - {response.text}")

    tts_done = time.time()
    print(f"[計測] Aivis合成完了: {tts_done:.3f} (経過: {tts_done - start_time:.3f} 秒)")

    # 一時ファイルに保存
    ext = ".mp3" if OUTPUT_FORMAT == "mp3" else ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
        temp_file.write(response.content)
        return temp_file.name


def tts_to_wav_local(text,out_path="outputs/temp_audio/temp.wav"):
    start_time = time.time()
    print(f"[計測] OpenAIテキスト受信 → Aivis送信開始: {start_time:.3f}")

    # Step 1: 構文情報を含んだクエリ作成
    query_response = _session.post(
        f"{AIVIS_LOCAL_URL}/audio_query",
        params={"text": text, "speaker": SPEAKER_ID}
     )

    query_response.raise_for_status()
    audio_query = query_response.json()

    
    if "speaker" in audio_query:
        print("audio_query に speaker を含めてはいけません")
        del audio_query["speaker"]

    # Step 2: それをそのまま synthesis に送信
    headers = {
        "Content-Type": "application/json"
    }

    synth_res = _session.post(
        f"{AIVIS_LOCAL_URL}/synthesis",
        params={"speaker": SPEAKER_ID},
        json=audio_query,
        headers=headers,
        timeout=60
    )

    synth_res.raise_for_status()
    
    tts_done = time.time()
    print(f"[計測] Aivis合成完了: {tts_done:.3f} (経過: {tts_done - start_time:.3f} 秒)")

    # wav 保存
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(synth_res.content)

    return out_path


def play_wav(file_path: str):
    print(f"[計測] 音声再生開始")
    data, samplerate = sf.read(file_path)
    sd.play(data, samplerate)
    sd.wait()
    end_time = time.time()
    print(f"[計測] 再生終了: {end_time:.3f}")

def speak(text: str):
    if ENGINE_MODE == "cloud" :
        wav_path = tts_to_wav(text)
    else:
        wav_path = tts_to_wav_local(text)
    play_wav(wav_path)
