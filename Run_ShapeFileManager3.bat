@echo off
setlocal
cd /d "%~dp0"
python SFM30.py
if errorlevel 1 pause
