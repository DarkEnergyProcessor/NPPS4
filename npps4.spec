# -*- mode: python ; coding: utf-8 -*-
import os.path
import pathlib
import shutil

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    DISTPATH: str = ""
    from PyInstaller.building.build_main import Analysis
    from PyInstaller.building.api import COLLECT, EXE, PYZ
from PyInstaller.building.datastruct import Tree
from PyInstaller.utils.hooks import collect_submodules, copy_metadata

a = Analysis(
    ["pyinstaller_bootstrap.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("alembic.ini", "."),
        *[
            (src, pathlib.Path(dst or src).parent)
            for src, dst, _ in Tree(
                "npps4/alembic",
                prefix="npps4/alembic",
                excludes=["__pycache__", "*.pyc", "*.pyo"],
            )
        ],
        *copy_metadata("npps4"),
    ],
    hiddenimports=[
        "aiosqlite",
        "psycopg",
        "winloop._noop",
        "npps4.scriptutils.boot",
        "npps4.scriptutils.user",
        "npps4.script_dummy",
        *collect_submodules("npps4"),
    ],
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
    name="npps4",
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
    name="npps4",
)

# Copy runtime files beside the executable.
target_dir = os.path.join(DISTPATH, coll.name)
os.makedirs(target_dir, exist_ok=True)

# Copy external files.
for src in ["beatmaps", "external", "scripts", "static", "templates"]:
    shutil.copytree(src, os.path.join(target_dir, src), dirs_exist_ok=True)

for src, dst in [
    ("default_server_key.pem", "server_key.pem"),
]:
    dest_path = os.path.join(target_dir, dst)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    shutil.copy2(src, dest_path)

# Build config.toml
with open("config.sample.toml", "r", encoding="utf-8", newline="") as f:
    _npps4_config = f.read()

_npps4_config = _npps4_config.replace(
    'server_private_key = "default_server_key.pem"', 'server_private_key = "server_key.pem"'
)

_dlapi_server = os.environ.get("NPPS4_CONFIG_DOWNLOAD_N4DLAPI_SERVER", "")
if _dlapi_server:
    _npps4_config = _npps4_config.replace('backend = "none"', 'backend = "n4dlapi"').replace(
        'server = "https://localhost:8000"', f'server = "{_dlapi_server}"'
    )

with open(f"{target_dir}/config.toml", "w", encoding="utf-8", newline="") as f:
    f.write(_npps4_config)
