from setuptools import setup

APP = ['src/main.py']
DATA_FILES = [
    ('assets', ['assets/icon.icns', 'assets/logo.png']),
]
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'assets/icon.icns',
    'plist': {
        'CFBundleName': 'SpeedAutoClicker',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
