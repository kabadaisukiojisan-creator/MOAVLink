@echo off
setlocal enabledelayedexpansion

REM このbatの場所を基準にしてパスを作る
set SCRIPT_DIR=%~dp0

REM "初期設定ツール\" を削って outputs を付ける
set BASE_DIR=%SCRIPT_DIR:初期設定ツール\=%
set CONFIG_PATH=%BASE_DIR%config\config.ini

echo CONFIG_PATH=%CONFIG_PATH%

REM === ユーザーから記憶番号を入力で受け取る ===
set /p MEMORYLV=記憶番号を入力してください（例：1[短記憶]2[中期記憶]3[長期記憶]）:

REM === UTF-8 (BOMなし) + LF 改行で書き出すために PowerShell を使用 ===
powershell -Command ^
  "$memorylv= \"%MEMORYLV%\";" ^
  "$configPath = \"%CONFIG_PATH%\";" ^
  "$in = Get-Content -Encoding UTF8 -Path $configPath;" ^
  "$out = @(); $inChat = $false;" ^
  "foreach ($line in $in) {" ^
  "  if ($line -match '^\[MEMORY\]') { $inChat = $true; $out += $line; continue }" ^
  "  if ($inChat -and $line -match '^\[') { $inChat = $false }" ^
  "  if ($inChat -and $line -match '^memory_level\s*=') { $line = 'memory_level = ' + $memorylv }" ^
  "  $out += $line;" ^
  "};" ^
  "$writer = New-Object System.IO.StreamWriter($configPath, $false, [System.Text.UTF8Encoding]::new($false));" ^
  "foreach ($line in $out) { $writer.Write(\"$line`n\") }" ^
  "$writer.Close()"

echo.
echo 記憶番号を更新しました！
echo → %CONFIG_PATH%
pause
