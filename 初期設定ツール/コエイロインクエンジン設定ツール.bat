@echo off
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0

set BASE_DIR=%SCRIPT_DIR:�����ݒ�c�[��\=%
set CONFIG_PATH=%BASE_DIR%config\config.ini

echo CONFIG_PATH=%CONFIG_PATH%

:INPUT_LOOP
REM === ��������Ă����uwindows-directml�v�̃t�H���_���w�肵�Ă������� ===
REM === ��FC:\windows-directml ===
set /p COEIROINK_PATH=�t�H���_�̏ꏊ����͂��Ă�������:

set COEIROINKENGINE=%COEIROINK_PATH%\engine.exe

REM === ���s�t�@�C�������݂��邩�`�F�b�N ===
if exist "!COEIROINKENGINE!" (
    echo ���s�t�@�C����������܂���: !COEIROINKENGINE!
) else (
    echo [�G���[] ���͂��ꂽ�t�H���_�ɂ� engine.exe ��������܂���ł����B
    echo ������x���͂��Ă��������B
    goto INPUT_LOOP
)

echo COEIROINKENGINE=%COEIROINKENGINE%

REM === PowerShell�� [COEIROINKENGINE] �Z�N�V������ windows_directml ���㏑�� ===
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
echo COEIROINK�G���W���ƕR�Â����܂����I
pause
