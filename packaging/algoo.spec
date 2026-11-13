# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification for Algoo IDE (Linux, Windows, macOS).
Run from repository root: pyinstaller --clean --noconfirm packaging/algoo.spec
"""

import os
import sys

ROOT_DIR = os.path.abspath(os.getcwd())
sys.path.insert(0, ROOT_DIR)
from version import APP_NAME, __version__

datas = [
    (os.path.join(ROOT_DIR, "docs"), "docs"),
    (os.path.join(ROOT_DIR, "snippets"), "snippets"),
    (os.path.join(ROOT_DIR, "examples"), "examples"),
    (os.path.join(ROOT_DIR, "ui", "assets"), os.path.join("ui", "assets")),
]

hiddenimports = [
    "compiler.runtime",
    "compiler.transpiler",
    "compiler.validator",
    "numpy",
    "markdown",
    "fitz",
]

icon_png = os.path.join(ROOT_DIR, "ui", "assets", "logo.png")
icon_ico = os.path.join(ROOT_DIR, "ui", "assets", "logo.ico")
icon_icns = os.path.join(ROOT_DIR, "ui", "assets", "logo.icns")

if sys.platform.startswith("win") and os.path.exists(icon_ico):
    app_icon = icon_ico
elif sys.platform == "darwin" and os.path.exists(icon_icns):
    app_icon = icon_icns
elif os.path.exists(icon_png):
    app_icon = icon_png
else:
    app_icon = None

a = Analysis(
    [os.path.join(ROOT_DIR, "main.py")],
    pathex=[ROOT_DIR],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "scipy", "pandas"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="algoo" if not sys.platform.startswith("win") else "Algoo",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=app_icon,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Algoo",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name=f"{APP_NAME}.app",
        icon=app_icon,
        bundle_identifier="com.softsurgery.algoo",
        info_plist={
            "CFBundleName": APP_NAME,
            "CFBundleDisplayName": APP_NAME,
            "CFBundleShortVersionString": __version__,
            "CFBundleVersion": __version__,
            "NSHighResolutionCapable": True,
            "CFBundleDocumentTypes": [
                {
                    "CFBundleTypeName": "Algorithme Algoo",
                    "CFBundleTypeExtensions": ["algo", "alg"],
                    "CFBundleTypeRole": "Editor",
                }
            ],
        },
    )
