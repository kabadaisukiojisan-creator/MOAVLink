@echo off
REM ����bat�̏ꏊ����ɂ��ăp�X�����
set SCRIPT_DIR=%~dp0

REM "�����ݒ�c�[��\" ������� outputs ��t����
set BASE_DIR=%SCRIPT_DIR:�����ݒ�c�[��\=%
set OUTPUT_DIR=%BASE_DIR%outputs

echo OUTPUT_DIR=%OUTPUT_DIR%

REM ���������������[�h�Ɏg��
set /p QUERY=�����̕�������o���Ă�������: 

REM sqlite.py �����s�isqlite.py �� outputs ���j
python "%OUTPUT_DIR%\sqlite.py" "%OUTPUT_DIR%" "%QUERY%"

pause