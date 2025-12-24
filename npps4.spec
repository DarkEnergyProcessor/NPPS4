# -*- mode: python ; coding: utf-8 -*-
import importlib.util

a = Analysis(
    ['pyinstaller_bootstrap.py'],
    pathex=[],
    binaries=[],
    datas=[
        ("alembic.ini", "."),
        ("npps4/alembic", "npps4/alembic"),
    ],
    hiddenimports=["aiosqlite", "psycopg", "winloop._noop"],
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
    name='npps4',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
    name='npps4',
)
