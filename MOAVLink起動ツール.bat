@echo off
setlocal enabledelayedexpansion

REM ‚±‚Ìbat‚ÌêŠ‚ğŠî€‚Éconfig.ini‚Æmain.py‚ÌƒpƒX‚ğì‚é
set SCRIPT_DIR=%~dp0
set MAIN_SCRIPT=%SCRIPT_DIR%main.py

echo MOAVLink‚ğ‹N“®‚µ‚Ü‚·...
py -3.11 "%MAIN_SCRIPT%"

REM pause
