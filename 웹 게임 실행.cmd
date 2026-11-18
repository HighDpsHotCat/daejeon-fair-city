@echo off
cd /d "%~dp0"
python "%~dp0web_game.py"
if errorlevel 1 pause
