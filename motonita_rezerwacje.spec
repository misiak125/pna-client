# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

tkinter_data = collect_data_files('tkinter')
babel_data = collect_data_files('babel')

a = Analysis(
    ['main.py'],
    pathex=['.', './src', './src/utils/', './src/views/'],
    binaries=[],
    datas=[
        ('src/static/*', 'static'),
        ('src/static/splash.png', '.'),
        ('icon.ico', '.')
    ] + tkinter_data + babel_data,
    hiddenimports=[
        'tkinter.ttk',
        'tkinter.font',
        'tkinter.filedialog',
        'tkcalendar',
        'PIL.Image', 
        'PIL.ImageTk',
        'PIL._tkinter_finder',
        'reportlab.pdfgen',
        'reportlab.lib',
        'reportlab.rl_settings',
        'babel.numbers',
        'babel.dates',
        'dateutil.tz',
        'dateutil.parser',
        'requests',
        'keyring',
        'keyring.backends.Windows'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['sqlalchemy', 'pymysql', 'python-dotenv', 'flask'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PNA',
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
    icon='icon.ico',
    splash='src/static/splash.png'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PNA', 
)