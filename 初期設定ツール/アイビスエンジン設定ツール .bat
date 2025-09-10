@echo off
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0

set BASE_DIR=%SCRIPT_DIR:�����ݒ�c�[��\=%
set CONFIG_PATH=%BASE_DIR%config\config.ini

echo CONFIG_PATH=%CONFIG_PATH%

:INPUT_LOOP
REM === �uAivisSpeech-Engine�v�̃t�H���_���w�肵�Ă������� ===
REM === ��FC:\AivisSpeech-Engine ===
set /p AVIS_PATH=�t�H���_�̏ꏊ����͂��Ă�������:

set AIVISENGINE=%AVIS_PATH%\run.py

REM === ���s�t�@�C�������݂��邩�`�F�b�N ===
if exist "!AIVISENGINE!" (
    echo ���s�t�@�C����������܂���: !AIVISENGINE!
) else (
    echo [�G���[] ���͂��ꂽ�t�H���_�ɂ� engine.exe ��������܂���ł����B
    echo ������x���͂��Ă��������B
    goto INPUT_LOOP
)

echo AIVISENGINE=%AIVISENGINE%

REM === PowerShell�� [AIVISENGINE] �Z�N�V������ aivis_directml ���㏑�� ===
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
echo COEIROINK�G���W���ƕR�Â����܂����I
pause
