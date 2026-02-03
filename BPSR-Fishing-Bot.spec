# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for BPSR Fishing Bot GUI.
This creates a standalone Windows executable.
"""

import os
import sys

block_cipher = None

# Get the project root directory
project_root = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['main_gui.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        # Include template images
        ('src/fishbot/assets/templates', 'src/fishbot/assets/templates'),
        # Include mascot for splash screen
        ('maskot.png', '.'),
        ('maskot2.png', '.'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'cv2',
        'numpy',
        'mss',
        'pyautogui',
        'keyboard',
        'pywinctl',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'pandas',
        'scipy',
        'numpy.random', # Often heavy if not needed
        'notebook',
        'IPython',
        'unittest',
        'pydoc',
        'pdb',
        'distutils',
        'setuptools',
        'xml', # If not parsing XML
        'sqlite3', # If not using DB
        'email',
        'http', # If no web requests
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
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
    name='Pelanggan Glenn Itu Lagi v4',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,  # Request administrator privileges
    icon='app_icon.ico',
)
