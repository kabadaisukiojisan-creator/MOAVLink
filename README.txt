【1. はじめに】

このアプリは、音声入力からOpenAI APIを介してキャラクター「任意のキャラクタ」の自然な応答を生成し、音声出力までを自動化する会話アプリです。
VOICEVOXのライセンス等の内容もあるため、商用化はする気はありません

作成した目的、現在ドール界隈でAIを使用して会話ができる機械が発売されたが、機械本体の値段が1万5千前後で毎月AIに1万近くの入金が必要だった
そんな高いお金を出して使いたくないので、自分で比較的安価のOpenAIを使用して似たようなものは作れないかと考え作成した
PCとBluetooth機能があるマイクとスピーカーとマクロキーボードがあればより安価で性能が良いAI会話ツールとして使用できるため、
コードを含めて公開することにする。
カバおじより賢い人がさらにツールを改良して使いやすくしてくれると助かる！


カバおじ考えている遠隔操作一式
マクロキーボード（Amazon）
https://www.amazon.co.jp/dp/B0BCJZPHTK/?coliid=I1ZVCTNOS4XHWS&colid=1H2FRGB9MXPNI&ref_=list_c_wl_lv_ov_lig_dp_it&th=1
iPoneを使用（SE2）
詳細は環境構築手順で説明

ビープ音等の音響は下記URLから転用しています
https://soundeffect-lab.info/sound/button/


【2. 必要なインストール（Python 3.11前提）】
※アプリ起動に必要な構築情報は環境構築手順.txtを参照してください



【3. 各 .py ファイルの説明】
ファイル名：機能概要
main.py                     ：アプリの起動/録音/応答生成/音声読み上げを統括
chat/gpt_client.py          ： OpenAIへのリクエストと応答取得、履歴保存処理
chat/conversation_manager.py： 会話ログの保存・まとめ処理
memory/vector_store.py      ： ベクトルDB（記憶）の管理と更新
recorder/speech_to_text.py  ： 音声をテキストに変換し疑問文処理も行う
voice/voicevox_client.py    ： 返答テキストをVOICEVOXで音声変換し再生する
tool/*.py                   ： マイクの一覧やインデックス取得に使用



【4. character_prompt.txt】
config/character_prompt.txt にてキャラ設定を制御。
内容は「設定したキャラ」として振る舞うためのプロンプト定義。
このテキストがOpenAIへ渡され、返答が「設定されたキャラ」らしくなります。



【5. 会話ログの保存・履歴の仕組み】
ログ種別	説明
outputs/conversation_log.json                ： 全ての会話履歴（ロール/時刻付き）
outputs/memory_logs/                         ： 記憶用途別に過去の会話を保存。
short_term.json/mid_term.json/long_term.json ： 短期記憶、中期記憶、長期記憶のOpenAIへ連携する付属情報
outputs/records/YYYYMMDD/                    ： 音声から変換された入力テキスト（一時ファイル）
outputs/responses/YYYYMMDD/                  ： OpenAIからの応答（一時ファイル）

現在は conversation_log.json にまとめ保存されるため、
records/responses は読み上げ後に削除されます。



【6. App.config 各定数の説明】

# ========== 共通設定 ==========
[GENERAL]
inputs_dir = outputs/inputs
responses_dir = outputs/responses
項目名：説明
inputs_dir   ：音声認識されたテキストの一時保存先（未使用時あり）
responses_dir：OpenAI応答の保存先（VOICEVOX読み上げに使用）

[RECORDER]
mic_device_index = 2
項目名：説明
mic_device_index ： 使用するマイクデバイスのインデックス番号（事前に確認必須）
                    接続しているマイクを検出しリスト化するツールと使用マイクの検知ツールを用意しているのそれらを使用し
                    マイクデバイスのインデックス番号を取得する（.../project_root/tool/フォルダの「list_microphones.py」と「mic_device_index.py」を使用すること

[CHAT]
character_prompt_file = config/character_prompt.txt
model = gpt-4o-mini
api_key = sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
項目名:説明
character_prompt_file： キャラクター性を保持するためのプロンプトファイルパス
model                ： 使用するOpenAIモデル（例：gpt-4o-mini）
api_key              ： OpenAIのAPIキー（漏洩注意！）
                        OpenAIにログイン情報を登録し、API_Keyを払い出し貼り付けてください。取得方法は別途説明あり

[VOICEVOX]
host = 127.0.0.1
port = 50021
speaker_id = 1
項目名:説明
host        ： VOICEVOXサーバーのホストアドレス（通常は 127.0.0.1）
port        ： VOICEVOXのポート番号（デフォルトは 50021）
speaker_id  ： 使用する話者ID（VOICEVOXで選択したキャラに応じて変更）

[KEYS]
record_key = f9
exit_key = esc
項目名：説明
record_key： 録音開始キー（デフォルト: F9）
exit_key  ： アプリ終了キー（デフォルト: ESC）

[MEMORY]
memory_level = 1
long_term_hits = 5
long_term_min_score = 0.3
mid_term_days = 3
項目名：説明
memory_level       ： 会話履歴の使用範囲を切り替える(0=記憶なし, 1=短期, 2=中期, 3=長期)
long_term_hits     ： 類似する会話履歴の件数上限（例：過去の類似質問を何件取り出すか）
long_term_min_score： ベクトル類似度の閾値（0.0?1.0）これより低いと記憶として採用しない
mid_term_days      ： 「中期記憶」の対象となる日数（例：3なら直近3日分を要約で取得）

[CONVERSATION]
question_suffixes = か,かな,ですか,の,ない,かい,って,のかな,なんで,いる,なに,なんやろ,なにだろ
項目名：説明
question_suffixes： 疑問符が最後に付けられる候補の文字列。ここで記載されている文字列が会話の最後尾についていた場合疑問符を付ける
