# FFMPEG Bulk Converter

This is a simple GUI tool for bulk converting video files from one format to another using `ffmpeg`.

## Features

*   Select input and output folders.
*   Choose video and audio codecs.
*   Select output file format.
*   Set video bitrate, with a dynamic option to match the input file's bitrate.
*   Option to cap the dynamic bitrate at a fallback value.
*   Option to delete input files after successful conversion.
*   Progress bar and log to monitor the conversion process.
*   Cancel button to stop the conversion.

## How to Use

1.  **Install FFmpeg:** This tool requires `ffmpeg` to be installed and accessible from your system's command line. You can download it from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html).
2.  **Run the application:**
    *   If you have the `.exe` file, simply double-click it to run.
    *   If you are running from the source code, run the command: `python converter_app.py`
3.  **Select Folders:** Use the "Browse..." buttons to select your input and output folders.
4.  **Choose Options:** Select your desired conversion options from the dropdown menus.
5.  **Start Conversion:** Click the "Start Conversion" button to begin the process.

## How to Build from Source

If you have made changes to the source code and want to build a new `.exe` file, follow these steps:

1.  **Install Dependencies:** Make sure you have all the required dependencies installed:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run PyInstaller:** Run the following command in the project's root directory:
    ```bash
    python -m PyInstaller --onefile --windowed --name=ffmpeg-converter converter_app.py
    ```
3.  **Find the Executable:** The new `ffmpeg-converter.exe` file will be located in the `dist` directory.
