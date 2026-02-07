#!/usr/bin/env bash
set -euo pipefail

# Build script for macOS using PyInstaller
# Produces: dist/CopyPasteTool/CopyPasteTool.app and CopyPasteTool.dmg

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

# Ensure pyinstaller is available
if ! command -v pyinstaller >/dev/null 2>&1; then
  echo "PyInstaller not found. Please install it in your active venv: pip install pyinstaller"
  exit 1
fi

# Name of the app
APP_NAME="CopyPasteTool"
ENTRY="clipboard_manager/main.py"

# Clean previous builds
rm -rf build/ dist/ "$APP_NAME.spec"

# PyInstaller build (onedir, windowed)
# --noconfirm to overwrite
pyinstaller --noconfirm --name "$APP_NAME" --windowed --onedir "$ENTRY"

# The .app bundle will be inside dist/CopyPasteTool/CopyPasteTool.app
APP_BUNDLE_DIR="dist/${APP_NAME}/${APP_NAME}.app"
if [ ! -d "$APP_BUNDLE_DIR" ]; then
  echo "ERROR: expected app bundle at $APP_BUNDLE_DIR but not found"
  ls -la dist || true
  exit 2
fi

# Create a compressed dmg using hdiutil
DMG_NAME="${APP_NAME}.dmg"
if [ -f "$DMG_NAME" ]; then
  rm -f "$DMG_NAME"
fi

hdiutil create -volname "$APP_NAME" -srcfolder "$APP_BUNDLE_DIR" -ov -format UDZO "$DMG_NAME"

echo "Build complete:"
echo "  App bundle: $APP_BUNDLE_DIR"
echo "  DMG: $ROOT_DIR/$DMG_NAME"

