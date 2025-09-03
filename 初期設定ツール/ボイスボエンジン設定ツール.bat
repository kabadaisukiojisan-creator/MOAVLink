@echo off
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0

set BASE_DIR=%SCRIPT_DIR:�����ݒ�c�[��\=%
set CONFIG_PATH=%BASE_DIR%config\config.ini

echo CONFIG_PATH=%CONFIG_PATH%

:INPUT_LOOP
REM === ��������Ă����uwindows-directml�v�̃t�H���_���w�肵�Ă������� ===
REM === ��FC:\windows-directml ===
set /p VOICEVOXENGINE_PATH=�t�H���_�̏ꏊ����͂��Ă�������:

set VOICEVOXENGINE=%VOICEVOXENGINE_PATH%\run.exe

REM === ���s�t�@�C�������݂��邩�`�F�b�N ===
if exist "!VOICEVOXENGINE!" (
    echo ���s�t�@�C����������܂���: !VOICEVOXENGINE!
) else (
    echo [�G���[] ���͂��ꂽ�t�H���_�ɂ� run.exe ��������܂���ł����B
    echo ������x���͂��Ă��������B
    goto INPUT_LOOP
)

echo VOICEVOXENGINE=%VOICEVOXENGINE%

REM === PowerShell�� [VOICEVOXENGINE] �Z�N�V������ windows_directml ���㏑�� ===
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
echo VOICEVOX�G���W���ƕR�Â����܂����I
pause
