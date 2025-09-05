@echo off
setlocal
setlocal enabledelayedexpansion


REM ����bat�̏ꏊ����ɂ��ăp�X�����
set SCRIPT_DIR=%~dp0

REM "�����ݒ�c�[��\" ������� outputs ��t����
set BASE_DIR=%SCRIPT_DIR:�����ݒ�c�[��\=%
set CONFIG_PATH=%BASE_DIR%config\config.ini
echo CONFIG_PATH=%CONFIG_PATH%


set "jsonFile=%APPDATA%\coeiroink-v2\speakerSettingStore.json"
set "logFile=%~dp0coeiroink_speaker_log.txt"

if not exist "%jsonFile%" (
    echo �t�@�C����������܂���: %jsonFile%
    pause
    exit /b 1
)


powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "try { $json = Get-Content -LiteralPath '%jsonFile%' -Raw -Encoding UTF8 | ConvertFrom-Json; foreach ($speaker in $json.speakerSetting) { Write-Output ('Speaker: ' + $speaker.speakerName); Write-Output ('  UUID : ' + $speaker.speakerUuid); foreach ($style in $speaker.styles) { Write-Output ('    Style: ' + $style.styleName + ' : ' + $style.styleId); }; Write-Output ''; } } catch { Write-Error $_ }"



REM === ���[�U�[����L�����N�^�[ID����͂Ŏ󂯎�� ===
set /p uuid=�ݒ肵�����L������UUID����͂��Ă��������i��F3c37646f-3881-5374-2a83-149267990abc[����݂����]�j:

REM === UTF-8 (BOM�Ȃ�) + LF ���s�ŏ����o�����߂� PowerShell ���g�p ===
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
echo �L�����N�^�[UUID���X�V���܂����I

REM === ���[�U�[����L�����N�^�[ID����͂Ŏ󂯎�� ===
set /p styleId=�ݒ肵�����L������Style����͂��Ă��������i��F0[�����ꂢ]�j:

REM === UTF-8 (BOM�Ȃ�) + LF ���s�ŏ����o�����߂� PowerShell ���g�p ===
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
echo �L�����N�^�[Style���X�V���܂����I

echo �� %CONFIG_PATH%

pause
endlocal