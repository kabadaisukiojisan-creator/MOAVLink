@echo off
REM このbatの場所を基準にしてパスを作る
set SCRIPT_DIR=%~dp0

REM "初期設定ツール\" を削って outputs を付ける
set BASE_DIR=%SCRIPT_DIR:初期設定ツール\=%
set OUTPUT_DIR=%BASE_DIR%outputs

echo OUTPUT_DIR=%OUTPUT_DIR%

REM 第一引数を検索ワードに使う
set /p QUERY=検索の文字列を出してください: 

REM sqlite.py を実行（sqlite.py は outputs 内）
python "%OUTPUT_DIR%\sqlite.py" "%OUTPUT_DIR%" "%QUERY%"

pause