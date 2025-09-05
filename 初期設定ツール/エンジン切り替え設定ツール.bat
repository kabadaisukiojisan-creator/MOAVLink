@echo off
setlocal enabledelayedexpansion

:: �X�N���v�g�̃f�B���N�g������ BASE_DIR ������
set "SCRIPT_DIR=%~dp0"
set "BASE_DIR=%SCRIPT_DIR:�����ݒ�c�[��\=%"
set "CONFIG_PATH=%BASE_DIR%config\config.ini"

if not exist "%CONFIG_PATH%" (
    echo config.ini ��������܂���: %CONFIG_PATH%
    pause
    exit /b 1
)

:: ���݂̃G���W�����m�F
for /f "usebackq delims=" %%A in (`
    powershell -NoProfile -Command ^
    "$in = Get-Content -Encoding UTF8 -Path '%CONFIG_PATH%'; foreach ($line in $in) { if ($line -match '^\s*engine\s*=\s*(\w+)') { $matches[1]; break } }"
`) do (
    set "CURRENT_ENGINE=%%A"
)

echo ���݂̃G���W���ݒ�: %CURRENT_ENGINE%

if /i "%CURRENT_ENGINE%"=="voicevox" (
    set "NEW_ENGINE=coeiroink"
    set "MESSAGE=VOICEVOX �� COEIROINK �ɐ؂�ւ��܂����H (y/n): "
) else if /i "%CURRENT_ENGINE%"=="coeiroink" (
    set "NEW_ENGINE=voicevox"
    set "MESSAGE=COEIROINK �� VOICEVOX �ɐ؂�ւ��܂����H (y/n): "
) else (
    echo �s���ȃG���W���ݒ�ł�: %CURRENT_ENGINE%
    pause
    exit /b 1
)

set /p ANSWER=%MESSAGE%
if /i "%ANSWER%" NEQ "y" (
    echo �L�����Z�����܂����B�ݒ�͕ύX����܂���B
    pause
    exit /b 0
)

echo engine �� %NEW_ENGINE% �ɐ؂�ւ��Ă��܂�...

:: �G���W���ݒ���������� (UTF-8�ێ�)
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

echo �������܂����I�V�����G���W���ݒ�: %NEW_ENGINE%
pause
endlocal
