@echo off
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0

set BASE_DIR=%SCRIPT_DIR:初期設定ツール\=%
set CONFIG_PATH=%BASE_DIR%config\config.ini

echo CONFIG_PATH=%CONFIG_PATH%

:INPUT_LOOP
REM === 同梱されていた「windows-directml」のフォルダを指定してください ===
REM === 例：C:\windows-directml ===
set /p COEIROINK_PATH=フォルダの場所を入力してください:

set COEIROINKENGINE=%COEIROINK_PATH%\engine.exe

REM === 実行ファイルが存在するかチェック ===
if exist "!COEIROINKENGINE!" (
    echo 実行ファイルが見つかりました: !COEIROINKENGINE!
) else (
    echo [エラー] 入力されたフォルダには engine.exe が見つかりませんでした。
    echo もう一度入力してください。
    goto INPUT_LOOP
)

echo COEIROINKENGINE=%COEIROINKENGINE%

REM === PowerShellで [COEIROINKENGINE] セクションの windows_directml を上書き ===
powershell -Command ^
  "$exePath = \"%COEIROINKENGINE%\";" ^
  "$configPath = \"%CONFIG_PATH%\";" ^
  "$in = Get-Content -Encoding UTF8 -Path $configPath;" ^
  "$out = @(); $inVVE = $false;" ^
  "foreach ($line in $in) {" ^
  "  if ($line -match '^\[COEIROINKENGINE\]') { $inVVE = $true; $out += $line; continue }" ^
  "  if ($inVVE -and $line -match '^\[') { $inVVE = $false }" ^
  "  if ($inVVE -and $line -match '^coeiroink_directml\s*=') { $line = 'coeiroink_directml = ' + $exePath }" ^
  "  $out += $line;" ^
  "};" ^
  "$writer = New-Object System.IO.StreamWriter($configPath, $false, [System.Text.UTF8Encoding]::new($false));" ^
  "foreach ($line in $out) { $writer.Write(\"$line`n\") }" ^
  "$writer.Close()"

echo.
echo COEIROINKエンジンと紐づけしました！
pause
