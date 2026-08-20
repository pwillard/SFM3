@echo off
setlocal
cd /d "%~dp0"

set "OUT=dist\SFM3.exe"
set "TMPDIST=%TEMP%\SFM3-build-%RANDOM%-%RANDOM%"

python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name SFM3 ^
  --icon "assets\SFM3_RSS.ico" ^
  --add-binary "orzip.exe;." ^
  --add-data "assets\SFM3.ico;assets" ^
  --add-data "assets\SFM3_icon.png;assets" ^
  --add-data "assets\SFM3_RSS.ico;assets" ^
  --add-data "assets\SFM3_RSS.png;assets" ^
  --distpath "%TMPDIST%" ^
  SFM30.py

if errorlevel 1 (
  rmdir /s /q "%TMPDIST%" >nul 2>nul
  pause
  exit /b 1
)

if not exist dist mkdir dist
copy /Y "%TMPDIST%\SFM3.exe" "%OUT%" >nul 2>nul
if errorlevel 1 (
  echo Built "%TMPDIST%\SFM3.exe"
  echo Unable to replace "%OUT%". Close any running SFM3.exe or file viewer, then copy the built file over the final EXE.
  pause
  exit /b 1
)

rmdir /s /q "%TMPDIST%" >nul 2>nul
echo %CD%\%OUT%
