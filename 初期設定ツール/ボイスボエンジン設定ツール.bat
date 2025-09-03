@echo off
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0

set BASE_DIR=%SCRIPT_DIR:初期設定ツール\=%
set CONFIG_PATH=%BASE_DIR%config\config.ini

echo CONFIG_PATH=%CONFIG_PATH%

:INPUT_LOOP
REM === 同梱されていた「windows-directml」のフォルダを指定してください ===
REM === 例：C:\windows-directml ===
set /p VOICEVOXENGINE_PATH=フォルダの場所を入力してください:

set VOICEVOXENGINE=%VOICEVOXENGINE_PATH%\run.exe

REM === 実行ファイルが存在するかチェック ===
if exist "!VOICEVOXENGINE!" (
    echo 実行ファイルが見つかりました: !VOICEVOXENGINE!
) else (
    echo [エラー] 入力されたフォルダには run.exe が見つかりませんでした。
    echo もう一度入力してください。
    goto INPUT_LOOP
)

echo VOICEVOXENGINE=%VOICEVOXENGINE%

REM === PowerShellで [VOICEVOXENGINE] セクションの windows_directml を上書き ===
powershell -Command ^
  "$exePath = \"%VOICEVOXENGINE%\";" ^
  "$configPath = \"%CONFIG_PATH%\";" ^
  "$in = Get-Content -Encoding UTF8 -Path $configPath;" ^
  "$out = @(); $inVVE = $false;" ^
  "foreach ($line in $in) {" ^
  "  if ($line -match '^\[VOICEVOXENGINE\]') { $inVVE = $true; $out += $line; continue }" ^
  "  if ($inVVE -and $line -match '^\[') { $inVVE = $false }" ^
  "  if ($inVVE -and $line -match '^windows_directml\s*=') { $line = 'windows_directml = ' + $exePath }" ^
  "  $out += $line;" ^
  "};" ^
  "$writer = New-Object System.IO.StreamWriter($configPath, $false, [System.Text.UTF8Encoding]::new($false));" ^
  "foreach ($line in $out) { $writer.Write(\"$line`n\") }" ^
  "$writer.Close()"

echo.
echo VOICEVOXエンジンと紐づけしました！
pause
