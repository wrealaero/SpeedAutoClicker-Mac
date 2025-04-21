from setuptools import setup
import os

# Application name and main script
APP_NAME = 'SpeedAutoClicker'
APP = ['src/main.py']

# Data files (icons, assets, and other resources)
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

# macOS-specific build options
OPTIONS = {
    # App packaging options
    'argv_emulation': False,  # Disabled for better compatibility with PyQt
    'strip': True,
    'optimize': 2,
    
    # Icon and metadata
    'iconfile': 'src/assets/icon.icns',
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': '© 2023 SpeedAutoClicker',
        'LSMinimumSystemVersion': '10.9',  # OS X Mavericks (your 2015 Mac supports this)
        'NSRequiresAquaSystemAppearance': False,
        'NSSupportsAutomaticGraphicsSwitching': True,
    },
    
    # Python modules to include
    'packages': [
        'pynput',
        'PyQt5',
        'requests'
    ],
    
    # Specific module includes
    'includes': [
        'sip',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'pynput.keyboard',
        'pynput.mouse',
        'requests.utils'
    ],
    
    # Exclude unnecessary modules to reduce size
    'excludes': [
        'tkinter',
        'numpy',
        'scipy',
        'pandas',
        'matplotlib'
    ],
    
    # Resource handling
    'resources': [
        'src/assets/icon.icns',
        'src/assets/logo.png'
    ],
    
    # For Intel Mac compatibility (your 2015 Mac)
    'arch': 'x86_64',
}

setup(
    name=APP_NAME,
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app', 'pyobjc'],
)
