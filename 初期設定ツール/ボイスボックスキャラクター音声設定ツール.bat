@echo off
setlocal enabledelayedexpansion

REM このbatの場所を基準にしてパスを作る
set SCRIPT_DIR=%~dp0

REM "初期設定ツール\" を削って outputs を付ける
set BASE_DIR=%SCRIPT_DIR:初期設定ツール\=%
set CONFIG_PATH=%BASE_DIR%config\config.ini

echo CONFIG_PATH=%CONFIG_PATH%

REM === ユーザーからキャラクターIDを入力で受け取る ===
set /p SPEAK=キャラクターIDを入力してください（例：1[ずんだもん]）:

REM === UTF-8 (BOMなし) + LF 改行で書き出すために PowerShell を使用 ===
powershell -Command ^
  "$speak_id= \"%SPEAK%\";" ^
  "$configPath = \"%CONFIG_PATH%\";" ^
  "$in = Get-Content -Encoding UTF8 -Path $configPath;" ^
  "$out = @(); $inChat = $false;" ^
  "foreach ($line in $in) {" ^
  "  if ($line -match '^\[VOICEVOX\]') { $inChat = $true; $out += $line; continue }" ^
  "  if ($inChat -and $line -match '^\[') { $inChat = $false }" ^
  "  if ($inChat -and $line -match '^speaker_id\s*=') { $line = 'speaker_id = ' + $speak_id }" ^
  "  $out += $line;" ^
  "};" ^
  "$writer = New-Object System.IO.StreamWriter($configPath, $false, [System.Text.UTF8Encoding]::new($false));" ^
  "foreach ($line in $out) { $writer.Write(\"$line`n\") }" ^
  "$writer.Close()"

echo.
echo キャラクターIDを更新しました！
echo → %CONFIG_PATH%
pause
