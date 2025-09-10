@echo off
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0

set BASE_DIR=%SCRIPT_DIR:初期設定ツール\=%
set CONFIG_PATH=%BASE_DIR%config\config.ini

echo CONFIG_PATH=%CONFIG_PATH%

:INPUT_LOOP
REM === 「AivisSpeech-Engine」のフォルダを指定してください ===
REM === 例：C:\AivisSpeech-Engine ===
set /p AVIS_PATH=フォルダの場所を入力してください:

set AIVISENGINE=%AVIS_PATH%\run.py

REM === 実行ファイルが存在するかチェック ===
if exist "!AIVISENGINE!" (
    echo 実行ファイルが見つかりました: !AIVISENGINE!
) else (
    echo [エラー] 入力されたフォルダには engine.exe が見つかりませんでした。
    echo もう一度入力してください。
    goto INPUT_LOOP
)

echo AIVISENGINE=%AIVISENGINE%

REM === PowerShellで [AIVISENGINE] セクションの aivis_directml を上書き ===
powershell -Command ^
  "$exePath = \"%AIVISENGINE%\";" ^
  "$configPath = \"%CONFIG_PATH%\";" ^
  "$in = Get-Content -Encoding UTF8 -Path $configPath;" ^
  "$out = @(); $inVVE = $false;" ^
  "foreach ($line in $in) {" ^
  "  if ($line -match '^\[AIVISENGINE\]') { $inVVE = $true; $out += $line; continue }" ^
  "  if ($inVVE -and $line -match '^\[') { $inVVE = $false }" ^
  "  if ($inVVE -and $line -match '^aivis_directml\s*=') { $line = 'aivis_directml = ' + $exePath }" ^
  "  $out += $line;" ^
  "};" ^
  "$writer = New-Object System.IO.StreamWriter($configPath, $false, [System.Text.UTF8Encoding]::new($false));" ^
  "foreach ($line in $out) { $writer.Write(\"$line`n\") }" ^
  "$writer.Close()"

echo.
echo COEIROINKエンジンと紐づけしました！
pause
