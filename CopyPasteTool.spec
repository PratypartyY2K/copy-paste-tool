# -*- mode: python ; coding: utf-8 -*-

import os

ICON_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'icon.icns')
ICON_ARG = ICON_PATH if os.path.exists(ICON_PATH) else None


a = Analysis(
    ['clipboard_manager/main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CopyPasteTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CopyPasteTool',
)
app = BUNDLE(
    coll,
    name='CopyPasteTool.app',
    icon=ICON_ARG,
    bundle_identifier=None,
)
