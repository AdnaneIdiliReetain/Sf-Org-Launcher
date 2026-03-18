#!/usr/bin/env bash
# Build SF Org Launcher for macOS
# Output: dist/SF Org Launcher.app
set -e

echo "==> Installing build dependencies…"
pip3 install --quiet pyinstaller pillow pystray

echo "==> Building app…"
pyinstaller sf_org_launcher.spec --noconfirm

echo ""
echo "✅  Build complete!"
echo "    App: dist/SF Org Launcher.app"
echo ""
echo "To install, run: ./install.sh"
