# MOAVLink

MOAVLink は **音声認識 + OpenAI API + VOICEVOX or COEIROINK** を組み合わせて、キャラクターとの自然な会話を実現するオープンソースのツールです。  
F9キーで録音、ESCキーで終了というシンプルな操作で、音声の入出力と会話ログの保存を行います。

---

## 特徴
-  音声入力をリアルタイムでテキスト化
-  OpenAI API を用いた自然な応答生成
-  VOICEVOX or COEIROINK を使った音声出力
-  会話ログ・記憶機能付き（短期/中期/長期）
-  [![MOAVLink Demo](https://img.youtube.com/vi/gpfVaMXgogM/0.jpg)](https://youtu.be/gpfVaMXgogM)
- [![MOAVLink 公開動画](https://img.youtube.com/vi/ectvxXsy8-0/0.jpg)](https://www.youtube.com/watch?v=ectvxXsy8-0)
- ※全てパッケージ化したモノのは公開動画の説明欄にDLリンクを記載しております
 

---

## インストール
1. Python 3.11 をインストール
2. 本リポジトリをクローン
   ```bash
   git clone https://github.com/ユーザー名/MOAVLink.git
   cd MOAVLink\init\
   py -3.11 pip install -r requirements.txt


VOICEVOX エンジンを別途セットアップしてください
別途資料「環境構築手順.txt」を参照
※最低限の設定としては、API_KEYの設定とキャラクターの性格付けのみになります

使用方法

MOAVLink起動ツール.bat を実行

F9キーで録音開始、ESCキーで終了

会話ログは outputs/conversation_log.json に保存されます

---

## 音声合成エンジンについて

MOAVLink は複数の音声合成エンジンに対応しています。  
ユーザーの環境や用途に応じて選択できます。

### 対応エンジン
- **VoiceVox**（デフォルト）  
  無料で利用可能。ローカルで動作するため導入が簡単です。

- **Coeiroink**  
  高品質な音声合成と感情表現に対応。安定した利用が可能です。

- **Aivis Cloud API**  
  クラウド型の高速音声合成エンジンです。  
  PCに専用エンジンをインストールする必要がなく、APIキーとモデルUUIDを設定することで利用できます。  
  応答速度が非常に速く、自然なイントネーションが特徴です。  
  ※ 利用には [Aivis Project]("https://hub.aivis-project.com/cloud-api/dashboard?_gl=1*q5le33*_ga*MTY3NjYxNzA4LjE3NTcyODYzOTA.*_ga_TEMWCS6D7B*czE3NTcyOTgzODIkbzMkZzEkdDE3NTcyOTg2MzgkajQxJGwwJGgw") から APIキーを取得する必要があります。

### 切り替え方法
`初期設定ツールフォルダ` の `エンジン切り替え設定ツール.bat` で使用するエンジンを設定できます。



## 修正箇所

- Aivis Projectの使用を追加
- 環境構築BATの追加

## 現在のツリー構造
```text
./MOAVLink
│  LICENSE
│  LICENSE_JP.md
│  main.py                 ←修正
│  mainm_ethod.py          ←修正
│  MOAVLink起動ツール.bat
│  README.txt
│
├─chat
│      conversation_manager.py
│      gpt_client.py
│
├─config
│      character_prompt.txt
│      config.ini         ←修正
│
├─gui
│      conversation_viewer.py
│
├─init
│      requirements(full).txt
│      requirements.txt
│
├─memory
│      vector_store.py
│
├─outputs
│  │  conversation_log.json
│  │  gui_log.json
│  │  sqlite.py
│  │  vector_store.db
│  │
│  ├─memory_logs
│  │      long_term.json
│  │      mid_term.json
│  │      short_term.json
│  │
│  ├─records
│  ├─responses
│  └─temp_audio
│
├─recorder
│       speech_to_text.py
│
├─sounds
│      beep.wav
│      timeout.wav
│
├─tool
│      get_default_mic_id.py
│      list_microphones.py
│
├─voice
│     voicevox_client.py
│     coeiroink_client.py
│     aivis_client.py          ←追加
│
├─リファレンス
│      MOAVLink公開動画.pdf
│      MOAVLink公開動画.pptx
│      環境構築手順.txt
│
└─初期設定ツール
        API_KEY設定ツール.bat
        DB内容取得ツール.bat
        キャラクター音声設定ツール.bat
        ボイスボエンジン設定ツール.bat
        マイク設定ツール.bat
        初期化ツール.bat
        記憶設定変更ツール.bat
        エンジン切り替え設定ツール.bat  ←修正
        コエイロインクエンジン設定ツール.bat
        コエイロインクのキャラクター音声設定ツール.bat
        アイビスAPI_KEY設定ツール.bat   ←追加
        アイビスエンジン設定ツール .bat ←追加
```
---

## 注意

OpenAI API の利用には別途 API Key が必要です（各自取得してください）

Aivis Projectを使用する場合はAPI KEYが必要です（各自取得してください）
※クラウド版は現在封鎖されています(2025/09/10現在）使用できません
※キャラを変更したい場合は、Aivisの操作が必要になりますconfig.iniに記載していますので参照してください

VOICEVOX, COEIROINK, Aivisの利用はライセンスに従ってください

本プロジェクトは趣味・研究目的であり、商用利用は想定していません

## ライセンス
このプロジェクトは [MIT License](./LICENSE) の下で公開されています。  
参考訳として [日本語版](./LICENSE_JP.md) も用意しています。
