import pyaudio
import locale


def get_default_mic_id():
    """OSの規定マイクデバイスのIDを取得"""
    pa = pyaudio.PyAudio()
    default_index = None

    try:
        # OS規定の入力デバイスを取得
        default_index = pa.get_default_input_device_info().get("index")
        device_name = pa.get_default_input_device_info().get("name")
        
        encoding = locale.getpreferredencoding()
        safe_name = device_name.encode("utf-8", errors="ignore").decode(encoding, errors="ignore")
        print(f"規定のマイクID: {default_index} / デバイス名: {safe_name}")
        # print(f"規定のマイクID: {default_index} / デバイス名: {device_name}")
    except Exception as e:
        print("規定のマイクを取得できませんでした:", e)
    finally:
        pa.terminate()

    return default_index

if __name__ == "__main__":
    get_default_mic_id()
