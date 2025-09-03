@echo off
setlocal enabledelayedexpansion

REM ����bat�̏ꏊ����ɂ��ăp�X�����
set SCRIPT_DIR=%~dp0

REM "�����ݒ�c�[��\" ������� outputs ��t����
set BASE_DIR=%SCRIPT_DIR:�����ݒ�c�[��\=%
set CONFIG_PATH=%BASE_DIR%config\config.ini
set GET_MIC_LIST_PATH=%BASE_DIR%\tool\list_microphones.py
set GET_MIC_INDEX_PATH=%BASE_DIR%\tool\get_default_mic_id.py

REM == �}�C�N���X�g�ꗗ�\��
py -3.11 "%GET_MIC_LIST_PATH%"

REM == ���݂̋K��i�}�C�N�j��ID���擾
py -3.11 "%GET_MIC_INDEX_PATH%"

REM === ���[�U�[����MICID����͂Ŏ󂯎�� ===
set /p MIC_ID=�}�C�N��ID�����:

REM === UTF-8 (BOM�Ȃ�) + LF ���s�ŏ����o�����߂� PowerShell ���g�p ===
powershell -Command ^
  "$mic_id = \"%MIC_ID%\";" ^
  "$configPath = \"%CONFIG_PATH%\";" ^
  "$in = Get-Content -Encoding UTF8 -Path $configPath;" ^
  "$out = @(); $inChat = $false;" ^
  "foreach ($line in $in) {" ^
  "  if ($line -match '^\[RECORDER\]') { $inChat = $true; $out += $line; continue }" ^
  "  if ($inChat -and $line -match '^\[') { $inChat = $false }" ^
  "  if ($inChat -and $line -match '^mic_device_index\s*=') { $line = 'mic_device_index = ' + $mic_id }" ^
  "  $out += $line;" ^
  "};" ^
  "$writer = New-Object System.IO.StreamWriter($configPath, $false, [System.Text.UTF8Encoding]::new($false));" ^
  "foreach ($line in $out) { $writer.Write(\"$line`n\") }" ^
  "$writer.Close()"

echo.
echo �}�C�NID���X�V���܂����I
echo �� %CONFIG_PATH%
pause
