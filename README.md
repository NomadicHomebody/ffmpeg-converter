# FFMPEG Bulk Converter

This is a powerful GUI tool for bulk converting video files using `ffmpeg`, offering advanced controls and a user-friendly experience.

## Features

*   **Flexible Folder Selection:** Easily select input and output folders for your video conversions.
*   **Comprehensive Conversion Options:**
    *   **Video Codecs:** Choose from a wide range of video codecs, including NVIDIA-accelerated (hevc_nvenc, h264_nvenc, av1_nvenc), AV1, H.264, and H.265.
    *   **Audio Codecs:** Select between AAC and MP3 audio codecs.
    *   **Output Formats:** Convert to popular formats like MP4, MKV, and MOV.
    *   **Intelligent Bitrate Control:**
        *   **Dynamic Bitrate:** Automatically match the input file's bitrate.
        *   **Optimized Bitrate:** Select from predefined quality profiles (Max, High, Balanced, Low, Min Quality) that intelligently determine the best bitrate based on input video characteristics and desired output quality.
        *   **Fallback Bitrate:** Define a fallback bitrate to use if an optimized setting cannot be determined or if dynamic bitrate fails.
        *   **Bitrate Capping:** Option to cap dynamic or optimized bitrates at the specified fallback value.
*   **Concurrency Management:** Configure the number of simultaneous video conversions to optimize performance on your system.
*   **Enhanced Progress Reporting & Logging:**
    *   **Estimated Time Remaining (ETA):** Get real-time estimates for the completion of your conversion batch.
    *   **Verbose Logging:** Enable detailed `ffmpeg` output in the log area for advanced troubleshooting.
    *   **Save Log:** Export the entire conversion log to a text file.
    *   **Actual Output Details:** After each conversion, the log displays the actual bitrate, resolution, codecs, and format of the output file, ensuring transparency and quality verification.
    *   **Standardized & Color-Coded Logs:** Log messages are structured with timestamps and color-coded by type (info, success, error, warning, details) for improved readability and quick identification of critical events.
*   **Dynamic UI Scaling:** The application window is fully resizable, with the log area intelligently expanding to utilize available space, providing a comfortable viewing experience.
*   **Delete Input Files:** Option to automatically delete original input files after successful conversion.
*   **Cancellation:** Stop ongoing conversions at any time.

## How to Use

1.  **Install FFmpeg:** This tool requires `ffmpeg` to be installed and accessible from your system's command line. You can download it from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html).
2.  **Run the application:**
    *   If you have the `.exe` file, simply double-click it to run.
    *   If you are running from the source code, run the command: `python converter_app.py`
3.  **Select Folders:** Use the "Browse..." buttons to select your input and output folders.
4.  **Choose Options:** Select your desired conversion options from the dropdown menus. This now includes:
    *   **Video Bitrate:** Choose 'dynamic' to match input, 'optimized' for quality profiles, or a fixed bitrate.
    *   **Bitrate Quality Profile:** If 'optimized' is selected, choose your desired quality level (Max, High, Balanced, Low, Min).
    *   **Concurrent Conversions:** Set the number of files to convert simultaneously.
    *   **Enable Verbose Logging:** Check this for detailed `ffmpeg` output.
5.  **Start Conversion:** Click the "Start Conversion" button to begin the process.
6.  **Monitor Progress:** Observe the progress bar, ETA, and detailed logs. Use the "Save Log" button to export the log if needed.

## Configuration

The application uses a `bitrate_configs` directory to store JSON files that define the bitrate mappings for different quality profiles (e.g., `max_quality.json`, `balanced_quality.json`). This allows for easy customization and expansion of bitrate settings without modifying the core application code.

For detailed information on the structure of these configuration files and how to generate or customize them, please refer to the `bitrate_configs/README.md` file.

## How to Build from Source

If you have made changes to the source code and want to build a new `.exe` file, follow these steps:

1.  **Install Dependencies:** Make sure you have all the required dependencies installed:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Generate Bitrate Configs (if modified or new profiles needed):** If you have modified the `generate_bitrate_configs.py` script or need to regenerate the bitrate profile JSON files, run:
    ```bash
    python generate_bitrate_configs.py
    ```
3.  **Run PyInstaller:** Run the following command in the project's root directory:
    ```bash
    python -m PyInstaller --onefile --windowed --name=ffmpeg-converter converter_app.py
    ```
    *Note: Ensure the `bitrate_configs` directory is included in your PyInstaller build. PyInstaller typically includes directories referenced by the script automatically, but you might need to add `--add-data "bitrate_configs;bitrate_configs"` if issues arise.*
4.  **Find the Executable:** The new `ffmpeg-converter.exe` file will be located in the `dist` directory.
