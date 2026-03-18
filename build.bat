@echo off
REM Build SF Org Launcher for Windows
REM Output: dist\SF Org Launcher.exe

echo ==> Installing build dependencies...
pip install --quiet pyinstaller pillow pystray

echo ==> Building app...
pyinstaller sf_org_launcher.spec --noconfirm

echo.
echo Build complete!
echo    Exe: dist\SF Org Launcher.exe
echo.
echo To install, run: install.bat
