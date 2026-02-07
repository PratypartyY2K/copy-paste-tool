#!/usr/bin/env bash
set -euo pipefail

# Create an .icns file from the icon.iconset folder (macOS only)
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

ICONSET_DIR="assets/icon.iconset"
ICNS_OUT="assets/icon.icns"

if [ ! -d "$ICONSET_DIR" ]; then
  echo "icon.iconset directory not found under assets/. Create it and add required PNGs."
  exit 1
fi

if ! command -v iconutil >/dev/null 2>&1; then
  echo "iconutil not found. This script must run on macOS with iconutil available."
  exit 2
fi

iconutil -c icns "$ICONSET_DIR" -o "$ICNS_OUT"

echo "Wrote $ICNS_OUT"

