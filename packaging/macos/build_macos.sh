#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="python3"
PYINSTALLER_BIN="pyinstaller"
if [ -x "$ROOT_DIR/.venv/bin/python" ]; then
  PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
fi
if [ -x "$ROOT_DIR/.venv/bin/pyinstaller" ]; then
  PYINSTALLER_BIN="$ROOT_DIR/.venv/bin/pyinstaller"
fi

VERSION="$("$PYTHON_BIN" -c 'from version import __version__; print(__version__)')"
DMG_STAGE="$ROOT_DIR/build/dmg"
OUT_DMG="$ROOT_DIR/dist/Algoo-${VERSION}-macOS.dmg"

echo "Building PyInstaller macOS app bundle for Algoo v${VERSION}..."
"$PYINSTALLER_BIN" --clean --noconfirm packaging/algoo.spec

if [ ! -d "$ROOT_DIR/dist/Algoo.app" ]; then
  echo "Error: dist/Algoo.app was not generated." >&2
  exit 1
fi

rm -rf "$DMG_STAGE" "$OUT_DMG"
mkdir -p "$DMG_STAGE"
cp -R "$ROOT_DIR/dist/Algoo.app" "$DMG_STAGE/"
ln -s /Applications "$DMG_STAGE/Applications"

echo "Creating macOS DMG image at ${OUT_DMG}..."
hdiutil create \
  -volname "Algoo ${VERSION}" \
  -srcfolder "$DMG_STAGE" \
  -ov \
  -format UDZO \
  "$OUT_DMG"

echo "Created macOS installer: $OUT_DMG"
