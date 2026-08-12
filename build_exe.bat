@echo off
setlocal
cd /d "%~dp0"

python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name SFM3 ^
  --add-binary "orzip.exe;." ^
  SFM30.py

if errorlevel 1 pause
