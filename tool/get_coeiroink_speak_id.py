import requests
import json

host = "127.0.0.1"
port = 50021

response = requests.get(f"http://{host}:{port}/speakers")
speakers = response.json()

# わかりやすく整形して表示
print(json.dumps(speakers, indent=2, ensure_ascii=False))