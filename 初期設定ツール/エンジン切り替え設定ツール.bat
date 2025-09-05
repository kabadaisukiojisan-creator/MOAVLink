@echo off
setlocal enabledelayedexpansion

:: スクリプトのディレクトリから BASE_DIR を決定
set "SCRIPT_DIR=%~dp0"
set "BASE_DIR=%SCRIPT_DIR:初期設定ツール\=%"
set "CONFIG_PATH=%BASE_DIR%config\config.ini"

if not exist "%CONFIG_PATH%" (
    echo config.ini が見つかりません: %CONFIG_PATH%
    pause
    exit /b 1
)

:: 現在のエンジンを確認
for /f "usebackq delims=" %%A in (`
    powershell -NoProfile -Command ^
    "$in = Get-Content -Encoding UTF8 -Path '%CONFIG_PATH%'; foreach ($line in $in) { if ($line -match '^\s*engine\s*=\s*(\w+)') { $matches[1]; break } }"
`) do (
    set "CURRENT_ENGINE=%%A"
)

echo 現在のエンジン設定: %CURRENT_ENGINE%

if /i "%CURRENT_ENGINE%"=="voicevox" (
    set "NEW_ENGINE=coeiroink"
    set "MESSAGE=VOICEVOX → COEIROINK に切り替えますか？ (y/n): "
) else if /i "%CURRENT_ENGINE%"=="coeiroink" (
    set "NEW_ENGINE=voicevox"
    set "MESSAGE=COEIROINK → VOICEVOX に切り替えますか？ (y/n): "
) else (
    echo 不明なエンジン設定です: %CURRENT_ENGINE%
    pause
    exit /b 1
)

set /p ANSWER=%MESSAGE%
if /i "%ANSWER%" NEQ "y" (
    echo キャンセルしました。設定は変更されません。
    pause
    exit /b 0
)

echo engine を %NEW_ENGINE% に切り替えています...

:: エンジン設定を書き換え (UTF-8保持)
powershell -NoProfile -Command ^
  "$new = '%NEW_ENGINE%';" ^
  "$configPath = '%CONFIG_PATH%';" ^
  "$in = Get-Content -Encoding UTF8 -Path $configPath;" ^
  "$out = @();" ^
  "foreach ($line in $in) {" ^
  "  if ($line -match '^\s*engine\s*=') { $line = 'engine = ' + $new }" ^
  "  $out += $line;" ^
  "};" ^
  "$writer = New-Object System.IO.StreamWriter($configPath, $false, [System.Text.UTF8Encoding]::new($false));" ^
  "foreach ($line in $out) { $writer.Write(\"$line`n\") }" ^
  "$writer.Close()"

echo 完了しました！新しいエンジン設定: %NEW_ENGINE%
pause
endlocal
