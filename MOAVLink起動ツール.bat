@echo off
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set MAIN_SCRIPT=%SCRIPT_DIR%main.py

echo MOAVLink���N�����܂�...
py -3.11 "%MAIN_SCRIPT%"
