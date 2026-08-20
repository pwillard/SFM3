# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['SFM30.py'],
    pathex=[],
    binaries=[('orzip.exe', '.')],
    datas=[('assets/SFM3.ico', 'assets'), ('assets/SFM3_icon.png', 'assets'), ('assets/SFM3_RSS.ico', 'assets'), ('assets/SFM3_RSS.png', 'assets')],
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
    a.binaries,
    a.datas,
    [],
    name='SFM3',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/SFM3_RSS.ico'],
)
