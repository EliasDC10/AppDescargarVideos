# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

root = Path(SPECPATH)
suffix = ".exe" if sys.platform == "win32" else ""
binaries = []
for source, destination in (
    (root / "ffmpeg" / f"ffmpeg{suffix}", "ffmpeg"),
    (root / "tools" / f"yt-dlp{suffix}", "tools"),
):
    if source.is_file():
        binaries.append((str(source), destination))

a = Analysis(
    [str(root / "main.py")],
    pathex=[str(root)],
    binaries=binaries,
    datas=collect_data_files("customtkinter"),
    hiddenimports=collect_submodules("yt_dlp"),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Descargador de Videos",
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
collection = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Descargador de Videos",
)

if sys.platform == "darwin":
    app = BUNDLE(
        collection,
        name="Descargador de Videos.app",
        icon=None,
        bundle_identifier="com.elias.descargadordevideos",
        version="2.0.0",
        info_plist={"NSHighResolutionCapable": True},
    )
