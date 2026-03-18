#!/usr/bin/env bash
# Install SF Org Launcher on macOS
#   1. Copies the .app to /Applications
#   2. Registers a LaunchAgent so it starts at login
set -e

APP_NAME="SF Org Launcher"
APP_SRC="dist/${APP_NAME}.app"
APP_DEST="/Applications/${APP_NAME}.app"
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="${PLIST_DIR}/com.sforg.launcher.plist"

# --- Check build exists ---
if [ ! -d "$APP_SRC" ]; then
    echo "❌  ${APP_SRC} not found. Run ./build.sh first."
    exit 1
fi

# --- Copy to /Applications ---
echo "==> Copying to /Applications…"
rm -rf "$APP_DEST"
cp -R "$APP_SRC" "$APP_DEST"
echo "    ✅  Installed at ${APP_DEST}"

# --- Create LaunchAgent for auto-start ---
echo "==> Setting up launch at login…"
mkdir -p "$PLIST_DIR"

cat > "$PLIST_FILE" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.sforg.launcher</string>
    <key>ProgramArguments</key>
    <array>
        <string>open</string>
        <string>-a</string>
        <string>SF Org Launcher</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/dev/null</string>
    <key>StandardErrorPath</key>
    <string>/dev/null</string>
</dict>
</plist>
EOF

echo "    ✅  LaunchAgent created at ${PLIST_FILE}"
echo ""
echo "🎉  Done! ${APP_NAME} will start automatically on your next login."
echo "    To start it now:  open -a '${APP_NAME}'"
