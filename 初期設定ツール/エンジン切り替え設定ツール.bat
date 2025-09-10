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
echo ============================
echo  音声エンジン切り替え番号
echo ============================
echo.
echo 1 : VoiceVox
echo 2 : Coeiroink
echo 3 : Aivis
echo.
set /p choice=番号を入力してください (1-3): 

if "%choice%"=="1" (
    set "NEW_ENGINE=voicevox"
) else if "%choice%"=="2" (
    set "NEW_ENGINE=coeiroink"
) else if "%choice%"=="3" (
    set "NEW_ENGINE=aivis"
) else (
    echo 不明なエンジン設定です: %CURRENT_ENGINE%
    pause
    exit /b 1
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
