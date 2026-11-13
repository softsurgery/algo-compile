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
ARCH="${DEB_ARCH:-$(dpkg --print-architecture 2>/dev/null || echo amd64)}"
PKG_NAME="algoo"
STAGE_DIR="$ROOT_DIR/build/deb/${PKG_NAME}_${VERSION}_${ARCH}"
OUT_DEB="$ROOT_DIR/dist/${PKG_NAME}_${VERSION}_${ARCH}.deb"

echo "Building PyInstaller bundle for Algoo v${VERSION}..."
"$PYINSTALLER_BIN" --clean --noconfirm packaging/algoo.spec

echo "Staging Debian package in ${STAGE_DIR}..."
rm -rf "$STAGE_DIR"
mkdir -p \
  "$STAGE_DIR/DEBIAN" \
  "$STAGE_DIR/opt/algoo" \
  "$STAGE_DIR/usr/bin" \
  "$STAGE_DIR/usr/share/applications" \
  "$STAGE_DIR/usr/share/icons/hicolor/256x256/apps"

cp -a "$ROOT_DIR/dist/Algoo/." "$STAGE_DIR/opt/algoo/"

cat > "$STAGE_DIR/usr/bin/algoo" <<'EOF'
#!/usr/bin/env bash
exec /opt/algoo/algoo "$@"
EOF
chmod 0755 "$STAGE_DIR/usr/bin/algoo"

cat > "$STAGE_DIR/usr/share/applications/algoo.desktop" <<'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Algoo
GenericName=IDE Algorithmique
Comment=Environnement de développement moderne et pédagogique pour l'Algorithmique
Exec=/usr/bin/algoo %F
Icon=algoo
Terminal=false
Categories=Development;IDE;Education;
StartupWMClass=Algoo
MimeType=text/x-algo;
EOF

cp "$ROOT_DIR/ui/assets/logo.png" "$STAGE_DIR/usr/share/icons/hicolor/256x256/apps/algoo.png"

INSTALLED_SIZE="$(du -sk "$STAGE_DIR/opt/algoo" | awk '{print $1}')"

cat > "$STAGE_DIR/DEBIAN/control" <<EOF
Package: ${PKG_NAME}
Version: ${VERSION}
Section: devel
Priority: optional
Architecture: ${ARCH}
Installed-Size: ${INSTALLED_SIZE}
Maintainer: softsurgery <contact@softsurgery.org>
Homepage: https://github.com/softsurgery/algoo
Description: IDE Algorithmique moderne et pédagogique
 Algoo est un environnement de développement intégré pour l'apprentissage
 de l'algorithmique avec compilation vers Python 3 + NumPy, inspecteurs
 TDO/TDNT et guide interactif.
EOF

mkdir -p "$ROOT_DIR/dist"
dpkg-deb --build --root-owner-group "$STAGE_DIR" "$OUT_DEB"
echo "Created Debian package: $OUT_DEB"
