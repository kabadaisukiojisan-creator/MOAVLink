@echo off
setlocal enabledelayedexpansion

REM このbatの場所を基準にしてパスを作る
set SCRIPT_DIR=%~dp0

REM "初期設定ツール\" を削って outputs を付ける
set BASE_DIR=%SCRIPT_DIR:初期設定ツール\=%
set CONFIG_PATH=%BASE_DIR%config\config.ini
set GET_MIC_LIST_PATH=%BASE_DIR%\tool\list_microphones.py
set GET_MIC_INDEX_PATH=%BASE_DIR%\tool\get_default_mic_id.py

REM == マイクリスト一覧表示
py -3.11 "%GET_MIC_LIST_PATH%"

REM == 現在の規定（マイク）のIDを取得
py -3.11 "%GET_MIC_INDEX_PATH%"

REM === ユーザーからMICIDを入力で受け取る ===
set /p MIC_ID=マイクのIDを入力:

REM === UTF-8 (BOMなし) + LF 改行で書き出すために PowerShell を使用 ===
powershell -Command ^
  "$mic_id = \"%MIC_ID%\";" ^
  "$configPath = \"%CONFIG_PATH%\";" ^
  "$in = Get-Content -Encoding UTF8 -Path $configPath;" ^
  "$out = @(); $inChat = $false;" ^
  "foreach ($line in $in) {" ^
  "  if ($line -match '^\[RECORDER\]') { $inChat = $true; $out += $line; continue }" ^
  "  if ($inChat -and $line -match '^\[') { $inChat = $false }" ^
  "  if ($inChat -and $line -match '^mic_device_index\s*=') { $line = 'mic_device_index = ' + $mic_id }" ^
  "  $out += $line;" ^
  "};" ^
  "$writer = New-Object System.IO.StreamWriter($configPath, $false, [System.Text.UTF8Encoding]::new($false));" ^
  "foreach ($line in $out) { $writer.Write(\"$line`n\") }" ^
  "$writer.Close()"

echo.
echo マイクIDを更新しました！
echo → %CONFIG_PATH%
pause
