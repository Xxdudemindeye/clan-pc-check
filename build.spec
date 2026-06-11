block_cipher = None

a = Analysis(
    ['scanner.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['winreg'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ClanCheck',
    debug=False,
    strip=False,
    upx=True,
    console=False,
)
