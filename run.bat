@echo off
rem Launch the emulator on Windows: run.bat [options]
cd /d "%~dp0"
python src\main.py %*
