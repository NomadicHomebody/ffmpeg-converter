# GEMINI Project Context: ffmpeg-converter

## Project Overview

This project is a Python-based command-line interface (CLI) tool for bulk converting video files from `.mkv` to `.mp4` format. It is optimized for compatibility with Jellyfin media servers. The tool uses `ffmpeg` for the conversion process.

The project includes a main conversion script, a separate GUI progress window, and a suite of unit tests.

### Key Technologies
- **Language:** Python 3.8+
- **CLI Framework:** `click`
- **GUI:** `PySide6`
- **Logging:** `structlog`
- **Progress Bar:** `tqdm`
- **Testing:** `pytest`

### Architecture
The application is composed of two main parts:
1.  `mkv_mp4_bulk_converter.py`: The core CLI application that handles file discovery, `ffmpeg` command execution, and progress reporting.
2.  `progress_window.py`: A standalone GUI window that displays conversion progress. It communicates with the main script over a TCP socket.

## Building and Running

### 1. Environment Setup
It is recommended to use a Python virtual environment.

```bash
# Create a virtual environment
python -m venv .venv

# Activate the environment
# On Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# On macOS/Linux
source .venv/bin/activate
```

### 2. Install Dependencies
Install the required Python packages from `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 3. Running the Application
The main script is `mkv_mp4_bulk_converter.py`.

**Basic Usage:**
```bash
python mkv_mp4_bulk_converter.py <path_to_folder_with_mkv_files>
```

**With Terminal Progress:**
```bash
python mkv_mp4_bulk_converter.py <path_to_folder> --progress
```

**With GUI Progress Window:**
You need to run two separate processes.

First, start the progress window:
```bash
python progress_window.py
```

Then, run the converter with the `--progress-window` flag:
```bash
python mkv_mp4_bulk_converter.py <path_to_folder> --progress-window
```

## Development Conventions

### Testing
The project uses `pytest` for unit testing. Tests are located in the `test/` directory.

To run the tests:
```bash
pytest
```

### Logging
The application uses `structlog` for structured, JSON-formatted logs. This allows for more detailed and machine-readable log output.

### Coding Style
- The code follows standard Python conventions (PEP 8).
- Functions are type-hinted.
- The project uses `click` for creating a clean and well-documented CLI.
