@echo off
setlocal enabledelayedexpansion

REM このbatの場所を基準にしてパスを作る
set SCRIPT_DIR=%~dp0

REM "初期設定ツール\" を削って outputs を付ける
set BASE_DIR=%SCRIPT_DIR:初期設定ツール\=%
set CONFIG_PATH=%BASE_DIR%config\config.ini

echo CONFIG_PATH=%CONFIG_PATH%

REM === ユーザーからAPIキーを入力で受け取る ===
set /p API_KEY=APIキーを入力してください（sk-から始まるもの）:

REM === UTF-8 (BOMなし) + LF 改行で書き出すために PowerShell を使用 ===
powershell -Command ^
  "$apiKey = \"%API_KEY%\";" ^
  "$configPath = \"%CONFIG_PATH%\";" ^
  "$in = Get-Content -Encoding UTF8 -Path $configPath;" ^
  "$out = @(); $inChat = $false;" ^
  "foreach ($line in $in) {" ^
  "  if ($line -match '^\[CHAT\]') { $inChat = $true; $out += $line; continue }" ^
  "  if ($inChat -and $line -match '^\[') { $inChat = $false }" ^
  "  if ($inChat -and $line -match '^api_key\s*=') { $line = 'api_key = ' + $apiKey }" ^
  "  $out += $line;" ^
  "};" ^
  "$writer = New-Object System.IO.StreamWriter($configPath, $false, [System.Text.UTF8Encoding]::new($false));" ^
  "foreach ($line in $out) { $writer.Write(\"$line`n\") }" ^
  "$writer.Close()"

echo.
echo APIキーを更新しました！
echo → %CONFIG_PATH%
pause
