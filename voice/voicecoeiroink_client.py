# -*- coding: utf-8 -*-
# voice/coeiroink_client.py

import os
import io
import json
import time
import tempfile
import pykakasi
import requests
import configparser
import soundfile as sf
import simpleaudio as sa
import sounddevice as sd


# =========================
# 設定
# =========================
_config = configparser.ConfigParser()
_config.read("config/config.ini", encoding="utf-8")

if "COEIROINK" not in _config:
    raise RuntimeError("config.ini に [COEIROINK] セクションがありません。")

HOST = _config["COEIROINK"].get("host", "127.0.0.1")
PORT = _config["COEIROINK"].get("port", "50032")  # GUI版は 50032 相当
SPEAKER_UUID = _config["COEIROINK"].get("speaker_uuid", "0")
STYLE_ID = int(_config["COEIROINK"].get("style_id", "0"))
OUTPUT_SAMPLING_RATE = int(_config["COEIROINK"].get("outputSamplingRate", "24000"))

# パラメータは VOICEVOX とほぼ互換
SPEED_SCALE       = float(_config["COEIROINK"].get("speedScale", "1.0"))
PITCH_SCALE       = float(_config["COEIROINK"].get("pitchScale", "0.0"))
INTONATION_SCALE  = float(_config["COEIROINK"].get("intonationScale", "1.0"))
VOLUME_SCALE      = float(_config["COEIROINK"].get("volumeScale", "1.0"))
PRE_PHONEME_LEN   = float(_config["COEIROINK"].get("prePhonemeLength", "0.1"))
POST_PHONEME_LEN  = float(_config["COEIROINK"].get("postPhonemeLength", "0.1"))

# GUI版では pauseLength 明示指定が無くてもOK。項目があるなら反映
PAUSE_LENGTH      = _config["COEIROINK"].get("pauseLength", None)

BASE_URL = f"http://{HOST}:{PORT}"
TEMP_DIR = os.path.join("outputs", "temp_audio")
os.makedirs(TEMP_DIR, exist_ok=True)
TEMP_WAV = os.path.join(TEMP_DIR, "temp.wav")

_session = requests.Session()
_timeout = (10, 60)  # (connect, read)

# 漢字をひらがなに変換するコンバータ
kakasi = pykakasi.kakasi()
kakasi.setMode("J", "K")  # 漢字 → ひらがな
kakasi.setMode("K", "K")  # カタカナはそのまま
kakasi.setMode("H", "K")  # ひらがなはそのまま
converter = kakasi.getConverter()

def to_katakana(text: str) -> str:
    return converter.do(text)

def _synthesis(text: str) -> bytes:
    """COEIROINK で音声バイナリを生成"""
    payload = {
        "text": text,
        "speakerUuid": SPEAKER_UUID,
        "styleId": STYLE_ID,
        "speedScale": SPEED_SCALE,
        "pitchScale": PITCH_SCALE,
        "intonationScale": INTONATION_SCALE,
        "volumeScale": VOLUME_SCALE,
        "prePhonemeLength": PRE_PHONEME_LEN,
        "postPhonemeLength": POST_PHONEME_LEN,
        "pauseLength": PAUSE_LENGTH,
        "outputSamplingRate": OUTPUT_SAMPLING_RATE,
        "startTrimBuffer": 100,
        "endTrimBuffer": 200
    }

    r = _session.post(
        f"{BASE_URL}/v1/synthesis",
        json=payload,
        timeout=_timeout
    )
    r.raise_for_status()
    return r.content

def _play_wav_bytes(wav_bytes: bytes):
    try:
        data, sr = sf.read(io.BytesIO(wav_bytes))
        sd.play(data, sr)
        sd.wait()
    except Exception as e:
        print(f"[COEIROINK] 再生エラー: {e}")

def speak(text: str):
    """main.py から呼ばれるエントリ。text をそのまま1発合成して再生"""
    if not text:
        return
    try:
        replace_text = text.replace("ハ", "ワ").replace("ヘ", "エ").replace("ヲ", "オ")
        text_kana = to_katakana(replace_text)
        wav = _synthesis(text_kana)
        _play_wav_bytes(wav)
    except requests.exceptions.ConnectionError:
        print("[COEIROINK] 接続できませんでした。COEIROINK.exe が起動しているか、ポート設定をご確認ください。")
    except Exception as e:
        print(f"[COEIROINK] 音声合成エラー: {e}")
