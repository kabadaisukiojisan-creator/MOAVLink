# MOAVLink

MOAVLink は **音声認識 + OpenAI API + VOICEVOX** を組み合わせて、キャラクターとの自然な会話を実現するオープンソースのツールです。  
F9キーで録音、ESCキーで終了というシンプルな操作で、音声の入出力と会話ログの保存を行います。

---

## 特徴
-  音声入力をリアルタイムでテキスト化
-  OpenAI API を用いた自然な応答生成
-  VOICEVOX を使った音声出力
-  会話ログ・記憶機能付き（短期/中期/長期）
-  [![MOAVLink Demo](https://img.youtube.com/vi/gpfVaMXgogM/0.jpg)](https://youtu.be/gpfVaMXgogM)

---

## インストール
1. Python 3.11 をインストール
2. 本リポジトリをクローン
   ```bash
   git clone https://github.com/ユーザー名/MOAVLink.git
   cd MOAVLink
   pip install -r requirements.txt


VOICEVOX エンジンを別途セットアップしてください

初期設定

config/config.ini を編集し、必要な設定を行います。

OpenAI API Key を入力

使用するマイクデバイスインデックスを設定

VOICEVOX の host / port / speaker_id を指定

使用方法

start_app.bat を実行

F9キーで録音開始、ESCキーで終了

会話ログは outputs/conversation_log.json に保存されます

注意

OpenAI API の利用には別途 API Key が必要です（各自取得してください）

VOICEVOX の利用はライセンスに従ってください

本プロジェクトは趣味・研究目的であり、商用利用は想定していません

## ライセンス
このプロジェクトは [MIT License](./LICENSE) の下で公開されています。  
参考訳として [日本語版](./LICENSE_JP.md) も用意しています。