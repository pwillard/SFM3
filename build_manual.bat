@echo off
setlocal
cd /d "%~dp0"

python tools\build_manual_pdf.py

if errorlevel 1 pause
