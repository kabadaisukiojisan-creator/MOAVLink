@echo off
setlocal enabledelayedexpansion

REM ����bat�̏ꏊ����ɂ��ăp�X�����
set SCRIPT_DIR=%~dp0

REM "�����ݒ�c�[��\" ������� outputs ��t����
set BASE_DIR=%SCRIPT_DIR:�����ݒ�c�[��\=%
set CONFIG_PATH=%BASE_DIR%config\config.ini

echo CONFIG_PATH=%CONFIG_PATH%

REM === ���[�U�[����API�L�[����͂Ŏ󂯎�� ===
set /p API_KEY=API�L�[����͂��Ă��������isk-����n�܂���́j:

REM === UTF-8 (BOM�Ȃ�) + LF ���s�ŏ����o�����߂� PowerShell ���g�p ===
powershell -Command ^
  "$apiKey = \"%API_KEY%\";" ^
  "$configPath = \"%CONFIG_PATH%\";" ^
  "$in = Get-Content -Encoding UTF8 -Path $configPath;" ^
  "$out = @(); $inChat = $false;" ^
  "foreach ($line in $in) {" ^
  "  if ($line -match '^\[CHAT\]') { $inChat = $true; $out += $line; continue }" ^
  "  if ($inChat -and $line -match '^\[') { $inChat = $false }" ^
  "  if ($inChat -and $line -match '^api_key\s*=') { $line = 'api_key = ' + $apiKey }" ^
  "  $out += $line;" ^
  "};" ^
  "$writer = New-Object System.IO.StreamWriter($configPath, $false, [System.Text.UTF8Encoding]::new($false));" ^
  "foreach ($line in $out) { $writer.Write(\"$line`n\") }" ^
  "$writer.Close()"

echo.
echo API�L�[���X�V���܂����I
echo �� %CONFIG_PATH%
pause
