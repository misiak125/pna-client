# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

tkinter_data = collect_data_files('tkinter')
babel_data = collect_data_files('babel')

a = Analysis(
    ['main.py'],
    pathex=['.' , './src' , './src/utils/' , './src/views/'],
    binaries=[],
    datas=[
        ('src/static/*', 'static')
        (r'C:\Python311\tcl\*', 'tcl'),
        (r'C:\Python311\Lib\lib-tk\*', 'lib-tk'),
        ('src/static/splash.png', 'splash.png'),
        ('incon.ico', 'icon.ico')
    ] + tkinter_data + babel_data,
    hiddenimports=[
        'babel.numbers',
        'babel.dates',
        'PIL._tkinter_finder',
        'PIL.Image', 
        'PIL.ImageTk',
        'PIL._tkinter_finder',
        'reportlab.pdfgen',
        'reportlab.lib',
        'reportlab.rl_settings',
        'dateutil.tz',
        'dateutil.parser',
        'tkinter.filedialog',
        'tkinter.font',
        'tkcalendar',
        "tkinter.ttk", 
        "tkinter.font"
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
    name='motonita_rezerwacje',
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
    splash = 'src/static/splash.png'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='motonita_rezerwacje',
)
