from setuptools import setup
import os

# Main application script
APP = ['src/main.py']

# Data files (icons, assets)
DATA_FILES = [
    ('assets', [
        'src/assets/icon.icns',
        'src/assets/logo.png'
    ]),
    ('', [
        'src/version.py',
        'src/updater.py',
        'src/clicker.py',
        'src/hotkeys.py'
    ])
]

# macOS specific options
OPTIONS = {
    'argv_emulation': False,  # Disable argv emulation for better compatibility
    'iconfile': 'src/assets/icon.icns',
    'packages': ['PyQt5', 'pynput'],
    'plist': {
        'CFBundleName': 'SpeedAutoClicker',
        'CFBundleDisplayName': 'Speed Auto Clicker',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': '© 2023 Your Name',
        'NSRequiresAquaSystemAppearance': False,
    },
    'includes': ['sip', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
