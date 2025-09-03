@echo off
REM このbatの場所を基準にしてパスを作る
set SCRIPT_DIR=%~dp0

REM "初期設定ツール\" を削って outputs を付ける
set BASE_DIR=%SCRIPT_DIR:初期設定ツール\=%
set OUTPUT_DIR=%BASE_DIR%init\

REM requirements.txt を使って pip install
REM pip install -r "%OUTPUT_DIR%requirements.txt"
py -3.11 -m pip install -r "%OUTPUT_DIR%requirements.txt"

pause