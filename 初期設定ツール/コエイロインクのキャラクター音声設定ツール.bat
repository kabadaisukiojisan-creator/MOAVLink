@echo off
setlocal
setlocal enabledelayedexpansion


REM このbatの場所を基準にしてパスを作る
set SCRIPT_DIR=%~dp0

REM "初期設定ツール\" を削って outputs を付ける
set BASE_DIR=%SCRIPT_DIR:初期設定ツール\=%
set CONFIG_PATH=%BASE_DIR%config\config.ini
echo CONFIG_PATH=%CONFIG_PATH%


set "jsonFile=%APPDATA%\coeiroink-v2\speakerSettingStore.json"
set "logFile=%~dp0coeiroink_speaker_log.txt"

if not exist "%jsonFile%" (
    echo ファイルが見つかりません: %jsonFile%
    pause
    exit /b 1
)


powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "try { $json = Get-Content -LiteralPath '%jsonFile%' -Raw -Encoding UTF8 | ConvertFrom-Json; foreach ($speaker in $json.speakerSetting) { Write-Output ('Speaker: ' + $speaker.speakerName); Write-Output ('  UUID : ' + $speaker.speakerUuid); foreach ($style in $speaker.styles) { Write-Output ('    Style: ' + $style.styleName + ' : ' + $style.styleId); }; Write-Output ''; } } catch { Write-Error $_ }"



REM === ユーザーからキャラクターIDを入力で受け取る ===
set /p uuid=設定したいキャラのUUIDを入力してください（例：3c37646f-3881-5374-2a83-149267990abc[つくよみちゃん]）:

REM === UTF-8 (BOMなし) + LF 改行で書き出すために PowerShell を使用 ===
powershell -Command ^
  "$uu_id= \"%uuid%\";" ^
  "$configPath = \"%CONFIG_PATH%\";" ^
  "$in = Get-Content -Encoding UTF8 -Path $configPath;" ^
  "$out = @(); $inChat = $false;" ^
  "foreach ($line in $in) {" ^
  "  if ($line -match '^\[COEIROINK\]') { $inChat = $true; $out += $line; continue }" ^
  "  if ($inChat -and $line -match '^\[') { $inChat = $false }" ^
  "  if ($inChat -and $line -match '^speaker_uuid\s*=') { $line = 'speaker_uuid = ' + $uu_id }" ^
  "  $out += $line;" ^
  "};" ^
  "$writer = New-Object System.IO.StreamWriter($configPath, $false, [System.Text.UTF8Encoding]::new($false));" ^
  "foreach ($line in $out) { $writer.Write(\"$line`n\") }" ^
  "$writer.Close()"

echo.
echo キャラクターUUIDを更新しました！

REM === ユーザーからキャラクターIDを入力で受け取る ===
set /p styleId=設定したいキャラのStyleを入力してください（例：0[せいれい]）:

REM === UTF-8 (BOMなし) + LF 改行で書き出すために PowerShell を使用 ===
powershell -Command ^
  "$style_Id= \"%styleId%\";" ^
  "$configPath = \"%CONFIG_PATH%\";" ^
  "$in = Get-Content -Encoding UTF8 -Path $configPath;" ^
  "$out = @(); $inChat = $false;" ^
  "foreach ($line in $in) {" ^
  "  if ($line -match '^\[COEIROINK\]') { $inChat = $true; $out += $line; continue }" ^
  "  if ($inChat -and $line -match '^\[') { $inChat = $false }" ^
  "  if ($inChat -and $line -match '^style_id\s*=') { $line = 'style_id = ' + $style_Id }" ^
  "  $out += $line;" ^
  "};" ^
  "$writer = New-Object System.IO.StreamWriter($configPath, $false, [System.Text.UTF8Encoding]::new($false));" ^
  "foreach ($line in $out) { $writer.Write(\"$line`n\") }" ^
  "$writer.Close()"


echo.
echo キャラクターStyleを更新しました！

echo → %CONFIG_PATH%

pause
endlocal