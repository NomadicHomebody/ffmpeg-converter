# mkv-mp4-bulkConverter

## Overview

A Python CLI tool to bulk convert `.mkv` files to `.mp4` using ffmpeg, optimized for Jellyfin compatibility. Only `.mkv` files are processed and converted to `.mp4`; all other files in the folder are left untouched.

## Features

- Processes all `.mp4` and `.mkv` files in a folder to `.mp4` using ffmpeg.
- Video Codec: HEVC (`hevc_nvenc`)
- Audio Codec: AAC (`.aac`)
- Audio Bitrate: 192k
- Maintains quality while minimizing file size.
- Deletes original `.mkv` files after conversion.
- Progress bar, file count, and time estimate (if possible).

## Requirements

- Python 3.8+
- ffmpeg (binary or built from source)
- [click](https://pypi.org/project/click/)
- [tqdm](https://pypi.org/project/tqdm/)
- [structlog](https://pypi.org/project/structlog/)

Install Python dependencies:
```bash
pip install -r requirements.txt
```

## FFmpeg Installation

### Windows

**Recommended (Binary):**
- Download static builds: https://www.gyan.dev/ffmpeg/builds/
- Extract and add the `bin` directory to your system `PATH`.
- Verify:
  ```powershell
  ffmpeg -version
  ```

**Build from Source:**
- Install MSYS2: https://www.msys2.org/
- Follow official guide: https://ffmpeg.org/download.html#build-windows

### macOS

**Recommended (Binary):**
```bash
brew install ffmpeg
```

**Build from Source:**
- Install Xcode and Metal SDK:
  ```bash
  xcrun -sdk macosx metal -v
  ```
- Build steps:
  ```bash
  git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg
  cd ffmpeg
  ./configure
  make
  make install
  ffmpeg -version
  ```

### Linux (Debian/Ubuntu)

**Recommended (Binary):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Build from Source:**
```bash
git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg
cd ffmpeg
./configure
make
sudo make install
ffmpeg -version
```

## Usage

```bash
python mkv_mp4_bulk_converter.py <input_folder> [--dry-run] [--verbose] [--progress]
```

- Only `.mkv` files are converted and deleted.
- Other files (images, text, etc.) remain untouched.

### CLI Options

- `<input_folder>`: Path to the folder containing `.mkv` files.
- `--dry-run`: Simulate conversion without making changes.
- `--verbose`: Enable verbose output.
- `--progress`: Show progress reporting.
- `--help`: Show help message and exit.

### Example Commands

Convert all `.mkv` files in a folder:
```bash
python mkv_mp4_bulk_converter.py /path/to/input_folder
```

Simulate conversion (no files changed), show progress and verbose logs:
```bash
python mkv_mp4_bulk_converter.py /path/to/input_folder --dry-run --progress --verbose
```

## Example ffmpeg Command

```bash
ffmpeg -i input.mkv -c:v hevc_nvenc -crf 28 -c:a aac -b:a 192k output.mp4
```

## Troubleshooting

- Ensure ffmpeg is installed and available in your system `PATH`.
- For advanced build options, see [official ffmpeg documentation](https://ffmpeg.org/documentation.html).

## Local Development Setup

The following steps will help you create a clean, isolated Python environment and run the tool directly from VSCode.

1. **Create a virtual environment** (once per repository):
   ```powershell
   python -m venv .venv
   ```
   This creates a `.venv` folder in the project root.

2. **Activate the environment**:
   - **Windows PowerShell**:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - **Windows CMD**:
     ```cmd
     .\.venv\Scripts\activate.bat
     ```
   - **Unix / macOS**:
     ```bash
     source .venv/bin/activate
     ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure VSCode**
   - Open the command palette (`Ctrl+Shift+P`) and select **Python: Select Interpreter**.
   - Choose the interpreter located in `.venv\Scripts\python.exe` (Windows) or `.venv/bin/python` (Unix).
   - VSCode will now use the virtual environment for linting, debugging, and running the script.

5. **Run the script from VSCode**
    - Open a terminal in VSCode (``Ctrl+``) and ensure the virtual environment is activated (you should see `(.venv)` in the prompt).
    - Execute the script:
      ```powershell
      python mkv_mp4_bulk_converter.py <input_folder> --progress
      ```
    - Alternatively, create a `launch.json` in `.vscode` to debug the script:
      ```json
      {
        "version": "0.2.0",
        "configurations": [
          {
            "name": "Python: mkv_mp4_bulk_converter",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/mkv_mp4_bulk_converter.py",
            "args": ["${workspaceFolder}/input", "--progress"],
            "console": "integratedTerminal"
          }
        ]
      }
      ```

These steps ensure that you are running the tool in an isolated environment and that VSCode is correctly configured to use it.

## License

MIT