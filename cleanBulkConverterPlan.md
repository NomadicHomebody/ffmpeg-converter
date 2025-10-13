# FFMPEG Bulk Converter GUI Plan

This plan outlines the development of a Python-based GUI tool for bulk video conversion using ffmpeg.

## 1. Core Components & Functionality

*   **GUI Framework:** Use a cross-platform GUI library like Tkinter (standard library, good for simple UIs), PyQt, or Kivy.
*   **File/Folder Selection:** Implement buttons for users to select input and output folders.
*   **Conversion Options:**
    *   Dropdown for video codec selection. Must include: all NVIDIA supported codecs (e.g., hevc_nvenc, h264_nvenc), AV1, H.264, H.265. Default: hevc_nvenc.
    *   Dropdown for audio codec selection. Must include: AAC, MP3. Default: AAC.
    *   Dropdown for output file format. Must include: MP4, MKV, MOV.
    *   Dropdown for video bitrate selection with values from 10Mbps to 250Mbps in 10Mbps increments. Also include an option to dynamically use the bitrate of the input file.
*   **Conversion Process:**
    *   Scan the selected input directory for video files (non-recursively).
    *   For each video file, construct the appropriate `ffmpeg` command.
    *   Execute the `ffmpeg` command in a separate thread to avoid freezing the GUI.
    *   Display real-time progress of the conversion.
*   **State Management:** The application should be able to handle the state of the conversion, including pausing, resuming, and stopping the process.

## 2. UI/UX Flow

1.  **Main Window:**
    *   "Select Input Folder" button.
    *   "Select Output Folder" button.
    *   Display selected paths.
    *   Conversion options (codecs, format, bitrate).
    *   "Start Conversion" button.
    *   Progress bar.
    *   A log/status area to show ffmpeg output and conversion status for each file.
2.  **Conversion In Progress:**
    *   Disable input/option selection during conversion.
    *   "Cancel" or "Pause" button becomes active.
    *   Progress bar updates.
    *   Log area shows which file is currently being converted.
3.  **Conversion Complete:**
    *   "Done" message.
    *   Enable input/option selection for a new batch.

## 3. Technical Implementation Details

*   **Backend Logic:** A separate Python module to handle the ffmpeg command generation and execution. This will keep the business logic separate from the UI.
*   **Concurrency:** Use Python's `threading` or `multiprocessing` to run the ffmpeg processes in the background so the UI remains responsive.
*   **FFmpeg Dependency:** The application will rely on the user having `ffmpeg` installed and available in their system's PATH. The application should check for the presence of `ffmpeg` on startup and provide instructions if it's not found.
*   **Output File Naming:** By default, all newly converted videos will be prefixed with "z_". If a file with that name already exists, the tool will attempt to save the new file with a numeric suffix (e.g., "z_1filename.mp4", "z_2filename.mp4", etc.) until a unique filename is found.
*   **Error Handling:**
    *   Handle cases where `ffmpeg` is not found.
    *   Catch and display errors from the `ffmpeg` process.
    *   Handle invalid user inputs (e.g., non-numeric bitrate).

## 4. Packaging and Distribution (for Windows)

*   Use a tool like `PyInstaller` or `cx_Freeze` to package the Python application and its dependencies into a single executable (`.exe`) file for easy distribution on Windows.
*   Include a `README` with instructions on how to use the tool and the requirement of having `ffmpeg` installed.

## 5. Development Phases

1.  **Phase 1: Core Logic:**
    *   Develop the Python script that can take command-line arguments for input/output folders and conversion parameters and performs the conversion.
2.  **Phase 2: Basic GUI:**
    *   Build the main window with all the UI elements (buttons, dropdowns, etc.).
    *   Hook up the UI elements to the core logic.
3.  **Phase 3: Concurrency and Progress:**
    *   Implement threading to prevent the GUI from freezing.
    *   Add progress bar and log area functionality.
4.  **Phase 4: Packaging:**
    *   Package the application for Windows.
5.  **Phase 5: Refinements:**
    *   Add more advanced features like preset management, drag-and-drop, etc.
    *   Improve error handling and user feedback.

## 6. Enhancements

1. **Intelligent Bitrate Option**
    * Add new bitrate option in GUI named "optimized" that supports new logic
    * Core Logic: Based on input file's video codec, bitrate and resolution. Map to an appropriate bitrate of the set output codec that optimizes the compromise between quality and file size. Use the appropriate logical data structure to store these mappings. This logic should execute when the "optimized" bitrate value is selected in the GUI.
    * Research as needed to get the context required to handle file conversions for 1080p/4k resolution videos and mapping between the codecs H264, HVENC, and AV1 (get all other formats listed in the supported formats if possible)
2. **Concurrency**
    * Add new integer incrementer value in the GUI (has buttons to increase/decrease value by 1) that maps to the supported number of concurrent/parallel ffmpeg file conversions to process
    * Enhance the app to support concurrent executions of the ffmpeg file conversions required for processing all of the files in the input folder. The value provided in the GUI should set the limit to concurrent executions of ffmpeg that are supported.
3. **Enhanced Progress Reporting & Logging**
    * Enhance the current logging to extract an estimated time remaining value for completing the processing of all files
    * Provide more logging output from the actual underlying ffmpeg executions (verbose mode) if needed
4. **App Experience**
    * Improve the app window experience to support dynamic scaling based on window size