@echo off
REM ����bat�̏ꏊ����ɂ��ăp�X�����
set SCRIPT_DIR=%~dp0

REM "�����ݒ�c�[��\" ������� outputs ��t����
set BASE_DIR=%SCRIPT_DIR:�����ݒ�c�[��\=%
set OUTPUT_DIR=%BASE_DIR%init\

REM requirements.txt ���g���� pip install
REM pip install -r "%OUTPUT_DIR%requirements.txt"
py -3.11 -m pip install -r "%OUTPUT_DIR%requirements.txt"

pause