# -*- mode: python ; coding: utf-8 -*-
"""
Especificación de PyInstaller para Zernike GUI.
Empaqueta la aplicación PySide6 y sus módulos matemáticos en un ejecutable standalone.
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Recopilación de submódulos e importaciones ocultas requeridas
hidden_imports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'matplotlib.backends.backend_qtagg',
    'numpy',
    'pandas',
    'lib',
    'lib.zernike',
    'lib.matriz',
    'lib.io',
    'lib.visualizacion',
    'gui',
    'gui.main_window',
    'gui.worker',
    'gui.canvas',
    'gui.dialogs',
    'gui.styles',
    'gui.interferogram_dialog',
    'gui.engine_comparison_dialog',
    'gui.zernike_viewer_dialog',
    'gui.components',
    'gui.components.parameter_panel',
    'gui.components.control_bar_3d',
    'gui.components.base_3d_dialog',
    'gui.components.summary_tables',
    'gui.components.preset_manager',
    'gui.components.menu_bar',
]

# Datos adicionales (archivos de configuración y recursos gráficos)
datas = []
if os.path.exists('config'):
    datas.append(('config', 'config'))
if os.path.exists('assets'):
    datas.append(('assets', 'assets'))

icon_path = 'assets/icon.ico' if os.path.exists('assets/icon.ico') else None

a = Analysis(
    ['gui_app.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'IPython', 'notebook', 'jupyter'],
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
    name='zernike-gui',
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
    icon=icon_path,
)
