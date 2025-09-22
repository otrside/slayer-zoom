import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py', 
    '--onefile',
    '-n slayer',
    '-i=assets/icon.ico'
    ])
