# --- 追加: 先頭付近に import を揃える ---
import configparser, os, re, io, json, requests, sounddevice as sd, soundfile as sf
from concurrent.futures import ThreadPoolExecutor

# 設定読み込み
config = configparser.ConfigParser()
config.read("config/config.ini", encoding="utf-8")


# 他の調整パラメータも読み込み
if "VOICEVOX" not in config:
    raise RuntimeError("config.ini に [VOICEVOX] セクションがありません")

VOICEVOX_HOST = config["VOICEVOX"]["host"]
VOICEVOX_PORT = config["VOICEVOX"]["port"]
SPEAKER_ID = int(config["VOICEVOX"]["speaker_id"])
SPEED_SCALE= float(config["VOICEVOX"]["speedScale"])
PITCH_SCALE = float(config["VOICEVOX"]["pitchScale"])
INTONATION_SCALE = float(config["VOICEVOX"]["intonationScale"])
VOLUME_SCALE = float(config["VOICEVOX"]["volumeScale"])
PAUSE_LENGTH = float(config["VOICEVOX"]["pauseLength"])
PRE_PHONEME_LENGTH = float(config["VOICEVOX"]["prePhonemeLength"])
POST_PHONEME_LENGTH = float(config["VOICEVOX"]["postPhonemeLength"])

VOICEVOX_HOST = config["VOICEVOX"]["host"]
VOICEVOX_PORT = config["VOICEVOX"]["port"]
BASE_URL = f"http://{VOICEVOX_HOST}:{VOICEVOX_PORT}"

# 接続の再利用で速くする
_session = requests.Session()

def _to_number(x, cast=float, default=None):
    try:
        return cast(x)
    except Exception:
        return default if default is not None else cast(0)

def _apply_query_params(q):
    # ここで config の値を必ず数値にキャスト
    q["speedScale"]       = _to_number(SPEED_SCALE,       float, 1.0)
    q["pitchScale"]       = _to_number(PITCH_SCALE,       float, 0.0)
    q["intonationScale"]  = _to_number(INTONATION_SCALE,  float, 1.0)
    q["volumeScale"]      = _to_number(VOLUME_SCALE,      float, 1.0)
    q["pauseLength"]      = _to_number(PAUSE_LENGTH,      float, 0.1)
    q["prePhonemeLength"] = _to_number(PRE_PHONEME_LENGTH,float, 0.1)
    q["postPhonemeLength"]= _to_number(POST_PHONEME_LENGTH,float, 0.1)

    if q.get("kana") is None:
        q["enableInterrogativeUpspeak"] = True
    return q

def _synthesize_once(text_chunk: str) -> bytes:
    # audio_query
    aq = _session.post(
        f"{BASE_URL}/audio_query",
        params={"text": text_chunk, "speaker": int(SPEAKER_ID)},
        timeout=30
    )
    aq.raise_for_status()
    q = _apply_query_params(aq.json())

    # ★ 重要：json= で渡す（Content-Type: application/json を自動付与）
    sy = _session.post(
        f"{BASE_URL}/synthesis",
        params={"speaker": int(SPEAKER_ID)},
        json=q,
        timeout=60
    )
    sy.raise_for_status()
    return sy.content

def _play_wav_bytes(wav_bytes: bytes):
    data, sr = sf.read(io.BytesIO(wav_bytes))
    sd.play(data, sr)
    sd.wait()

def _split_sentences(text: str):
    # 「。！？？」や ? で文区切り（空白は除去）
    parts = [s.strip() for s in re.split(r'(?<=[。！？\?])', text) if s.strip()]
    return parts if parts else [text]

def speak(text: str):
    sentences = _split_sentences(text)

    # 1文先行で合成しておいて、再生と重ねる
    with ThreadPoolExecutor(max_workers=2) as ex:
        fut = None
        for s in sentences:
            nxt = ex.submit(_synthesize_once, s)
            if fut is not None:
                wav = fut.result()
                _play_wav_bytes(wav)
            fut = nxt
        if fut is not None:
            _play_wav_bytes(fut.result())
