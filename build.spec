# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# --- VOBERIX BUILD AYARLARI ---
APP_NAME = 'VOBERIX'
ICON_PATH = 'icon.ico'
OBF_DIST = 'obf_dist' 

# 1. Kaynak Yolu Ayarı
if os.path.exists(OBF_DIST):
    sys.path.insert(0, os.path.abspath(OBF_DIST))
    target_path = os.path.join(OBF_DIST, 'main.py')
    analysis_paths = [os.path.abspath(OBF_DIST)]
else:
    target_path = 'main.py'
    analysis_paths = [os.path.abspath('.')]

# 2. PyArmor Runtime Kontrolü
runtime_pkg_name = None
if os.path.exists(OBF_DIST):
    for item in os.listdir(OBF_DIST):
        if item.startswith('pyarmor_runtime') and os.path.isdir(os.path.join(OBF_DIST, item)):
            runtime_pkg_name = item
            break

# 3. CustomTkinter Verilerini Topla
datas = collect_data_files('customtkinter')

# 4. Varlıkları Ekle
datas += [
    ('sword.png', '.'),
    ('shield.png', '.'),
    ('restore.png', '.'),
    ('logo.png', '.'),
    ('icon.ico', '.'),
    ('arrows.png', '.'), 
    ('attack.png', '.')
]

# 5. Gizli Importlar (YENİ KÜTÜPHANELER EKLENDİ)
hiddenimports = [
    'PIL._tkinter_finder',
    'pydirectinput',
    'pyautogui',
    'keyboard',
    'requests',
    'mss',          # <--- EKLENDİ (Ekran Yakalama)
    'cv2',          # <--- EKLENDİ (OpenCV Görüntü İşleme)
    'numpy',        # <--- EKLENDİ (Matematiksel İşlemler)
    'ctypes',
    'threading',
    'json',
    'logging',
    'logging.handlers',
    'modules',
    'modules.splash',
    'modules.login',
    'modules.ui',
    'modules.keyauth',
    'modules.components.settings_window',
    'modules.components.toast',
    'modules.components.error_window',
    'modules.components.announcement',
    'modules.components.module_card',
    'modules.features.mage56',   
    'modules.features.archer35'  
]

if runtime_pkg_name:
    hiddenimports.append(runtime_pkg_name)

hiddenimports += collect_submodules('modules')
hiddenimports += collect_submodules('customtkinter')

block_cipher = None

a = Analysis(
    [target_path],
    pathex=analysis_paths,
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name=APP_NAME,
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
    icon=ICON_PATH
)