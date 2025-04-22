from setuptools import setup

APP = ['src/main.py']
DATA_FILES = [
    ('assets', ['src/assets/icon.icns', 'src/assets/logo.png']),
]
OPTIONS = {
    'iconfile': 'src/assets/icon.icns',
    'plist': {
        'CFBundleName': "SpeedAutoClicker",
        'CFBundleVersion': "1.0.0",
        'NSRequiresAquaSystemAppearance': False
    },
    'packages': ['pynput', 'PyQt5'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
