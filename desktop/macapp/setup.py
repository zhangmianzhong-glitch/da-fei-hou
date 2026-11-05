from setuptools import setup

APP = ['da_fei_hou.py']

DATA_FILES = [
    ('Resources', ['assets/README.txt']),
]

OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'CFBundleName': '大肥猴',
        'CFBundleDisplayName': '大肥猴',
        'CFBundleIdentifier': 'com.openclaw.dafeihou',
        'CFBundleShortVersionString': '0.1.0',
        'CFBundleVersion': '0.1.0',
        'LSUIElement': True,
        'NSHighResolutionCapable': True,
    },
    'packages': ['objc', 'Foundation', 'AppKit', 'AVFoundation'],
}

setup(
    name='dafeihou',
    app=APP,
    data_files=DATA_FILES,
    options=OPTIONS,
)
