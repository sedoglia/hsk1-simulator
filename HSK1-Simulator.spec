# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — produce un singolo EXE monolitico per Windows."""

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Dati dell'applicazione (JSON, foto, scene)
        ('hsk1sim/data',   'hsk1sim/data'),
        ('hsk1sim/assets', 'hsk1sim/assets'),
    ],
    hiddenimports=[
        # pyttsx3 TTS offline (backend Windows SAPI5)
        'pyttsx3.drivers',
        'pyttsx3.drivers.sapi5',
        'win32com',
        'win32com.client',
        'win32api',
        # edge-tts (tutti i sottomoduli)
        'edge_tts.communicate',
        'edge_tts.constants',
        'edge_tts.data_classes',
        'edge_tts.drm',
        'edge_tts.exceptions',
        'edge_tts.submaker',
        'edge_tts.typing',
        'edge_tts.util',
        'edge_tts.version',
        'edge_tts.voices',
        # pypinyin (dizionari interni)
        'pypinyin',
        'pypinyin.phrases_dict',
        'pypinyin.pinyin_dict',
        'pypinyin.contrib',
        'pypinyin.contrib.mmseg',
        'pypinyin.seg',
        'pypinyin.seg.mmseg',
        # Pillow / Tkinter
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.ttk',
        'tkinter.font',
        # asyncio / httpx usati da edge_tts
        'asyncio',
        'httpx',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # librerie inutilizzate — riducono la dimensione del binario
        'matplotlib', 'numpy', 'scipy', 'pandas',
        'IPython', 'jupyter', 'notebook',
        'PyQt5', 'PyQt6', 'wx',
        'pygame',
        'test', 'unittest',
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
    name='HSK1-Simulator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # UPX può causare falsi positivi negli antivirus
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,       # nessuna finestra console (app grafica)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
