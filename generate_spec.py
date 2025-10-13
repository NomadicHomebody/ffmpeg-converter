import sys
from PyInstaller.building import makespec

if __name__ == "__main__":
    original_argv = sys.argv
    sys.argv = [
        'pyi-makespec',
        '--onefile',
        '--windowed',
        '--name=ffmpeg-converter',
        'converter_app.py',
    ]
    makespec.main()
    sys.argv = original_argv
