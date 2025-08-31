# 使用ライブラリ: requests, configparser, json, io, sounddevice, soundfile

import requests
import configparser
import json
import io
import sounddevice as sd
import soundfile as sf

config = configparser.ConfigParser()
config.read("config/config.ini", encoding="utf-8")

VOICEVOX_HOST = config["VOICEVOX"]["host"]
VOICEVOX_PORT = config["VOICEVOX"]["port"]
SPEAKER_ID = int(config["VOICEVOX"]["speaker_id"])
SPEED_SCALE= float(config["VOICEVOX"]["speedScale"])
PITCH_SCALE = float(config["VOICEVOX"]["pitchScale"])
INTONATION_SCALE = float(config["VOICEVOX"]["intonationScale"])
VOLUME_SCALE = float(config["VOICEVOX"]["volumeScale"])
PAUSE_LENGTH = float(config["VOICEVOX"]["pauseLength"])
PRE_PHONEME_LENGTH = float(config["VOICEVOX"]["prePhonemeLength"])
POST_PHONEME_LENGHT = float(config["VOICEVOX"]["postPhonemeLength"])


BASE_URL = f"http://{VOICEVOX_HOST}:{VOICEVOX_PORT}"

def speak(text: str):
    try:
        # Audio Query
        query = requests.post(
            f"{BASE_URL}/audio_query",
            params={"text": text, "speaker": SPEAKER_ID}
        )
        query.raise_for_status()
        query_json = query.json()
        query_json["speedScale"] = SPEED_SCALE
        query_json["pitchScale"] = PITCH_SCALE
        query_json["intonationScale"] = INTONATION_SCALE
        query_json["volumeScale"] = VOLUME_SCALE
        query_json["pauseLength"] = PAUSE_LENGTH
        query_json["prePhonemeLength"] = PRE_PHONEME_LENGTH
        query_json["postPhonemeLength"] = POST_PHONEME_LENGHT

        # Synthesis 48kHz
        synthesis = requests.post(
            f"{BASE_URL}/synthesis",
            params={"speaker": SPEAKER_ID, "outputSamplingRate": 48000},
            json=query_json
        )
        synthesis.raise_for_status()

        # バイト列を直接読み込んで再生
        wav_bytes = io.BytesIO(synthesis.content)
        data, samplerate = sf.read(wav_bytes, dtype="int16")
        sd.play(data, samplerate)
        sd.wait()  # 再生が終わるまで待機

    except Exception as e:
        print("VOICEVOX再生エラー:", e)
