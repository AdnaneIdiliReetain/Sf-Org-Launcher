# -*- mode: python ; coding: utf-8 -*-
import sys

a = Analysis(
    ['org_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('logo.png', '.'),
        ('quick_pages.json', '.'),
    ],
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
    name='SF Org Launcher',
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
    icon='logo.ico' if sys.platform == 'win32' else 'logo.icns',
)

if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='SF Org Launcher.app',
        icon='logo.icns',
        bundle_identifier='com.sf-org-launcher',
        info_plist={
            'CFBundleShortVersionString': '1.0.0',
            'LSUIElement': True,
        },
    )
