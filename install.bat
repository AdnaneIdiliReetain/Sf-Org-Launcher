@echo off
REM Install SF Org Launcher on Windows
REM   1. Copies the .exe to %LOCALAPPDATA%\SF Org Launcher
REM   2. Adds a registry Run key so it starts at login

set "APP_NAME=SF Org Launcher"
set "APP_SRC=dist\%APP_NAME%.exe"
set "INSTALL_DIR=%LOCALAPPDATA%\%APP_NAME%"
set "APP_DEST=%INSTALL_DIR%\%APP_NAME%.exe"
set "REG_KEY=HKCU\Software\Microsoft\Windows\CurrentVersion\Run"

REM --- Check build exists ---
if not exist "%APP_SRC%" (
    echo ERROR: %APP_SRC% not found. Run build.bat first.
    exit /b 1
)

REM --- Copy to install directory ---
echo ==> Installing to %INSTALL_DIR%...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
copy /Y "%APP_SRC%" "%APP_DEST%" >nul
echo     Installed at %APP_DEST%

REM --- Register for startup ---
echo ==> Setting up launch at login...
reg add "%REG_KEY%" /v "%APP_NAME%" /t REG_SZ /d "\"%APP_DEST%\"" /f >nul 2>&1
echo     Registry startup entry added.

echo.
echo Done! %APP_NAME% will start automatically on your next login.
echo     To start it now, run: "%APP_DEST%"
