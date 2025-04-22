from setuptools import setup

APP = ['src/main.py']
DATA_FILES = [('assets', ['src/assets/icon.icns'])]
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'src/assets/icon.icns',
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
