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

### 6.1. Intelligent Bitrate Controls

1.  **"Optimized" Bitrate Option:**
    *   **GUI:** The bitrate dropdown will include a new option named "Optimized".
    *   **Core Logic:** When "Optimized" is selected, the application will determine the output bitrate based on the input file's resolution, video codec, and the selected output codec.
    *   **Research & Mapping:** The logic will use a predefined mapping table covering common codecs (H.264, HEVC, AV1, etc.) and resolutions (720p, 1080p, 1440p, 4k).
    *   **Mapping Data Structure:** A dictionary or similar structure will store these mappings, for example:
        ```
        # Example Bitrate Mapping
        {
            "720p": {
                "h264": {"hevc": "4Mbps", "av1": "3Mbps"},
                "hevc": {"h264": "6Mbps", "av1": "3.5Mbps"}
            },
            "1080p": {
                "h264": {"hevc": "8Mbps", "av1": "6Mbps"},
                "hevc": {"h264": "12Mbps", "av1": "7Mbps"}
            },
            "1440p": {
                "h264": {"hevc": "16Mbps", "av1": "12Mbps"},
                "hevc": {"h264": "24Mbps", "av1": "14Mbps"}
            },
            "4k": {
                "h264": {"hevc": "25Mbps", "av1": "20Mbps"},
                "hevc": {"h264": "35Mbps", "av1": "22Mbps"}
            }
        }
        ```

2.  **Fallback Bitrate:**
    *   **GUI:** A new input field, labeled "Fallback Bitrate (Mbps)", will be added. It will default to `20`.
    *   **Core Logic:** If the "Optimized" option is used but no specific mapping is found for an input video, this fallback bitrate will be used for the conversion.

### 6.2. Concurrency Management

1.  **Concurrency Control:**
    *   **GUI:** An integer input field (e.g., a spinner or text box with +/- buttons) labeled "Concurrent Conversions" will be added.
    *   **Settings:** The value will default to `2`, with a minimum of `1` and a maximum of `32`.
    *   **Core Logic:** The application will manage a pool of background workers to execute `ffmpeg` conversions in parallel, up to the limit set by this value.

2.  **Error Handling:**
    *   **Core Logic:** If a conversion fails within a concurrent batch, the error will be logged, but the application will continue processing the remaining files in the queue. The overall process will not be halted by a single file's failure.

### 6.3. Enhanced Progress Reporting & Logging

1.  **Estimated Time Remaining (ETA):**
    *   **GUI:** A label will display the estimated time remaining to complete the entire batch.
    *   **Core Logic:** The ETA will be calculated using a simple averaging method: `(Average time per completed file) * (Number of remaining files)`. The estimate will update as each file is completed.

2.  **Verbose Logging & Export:**
    *   **GUI:** A checkbox labeled "Enable Verbose Logging" will be added. When checked, the log area will display more detailed output from the underlying `ffmpeg` processes.
    *   **GUI:** A button labeled "Save Log" will be added. Clicking this will prompt the user to save the contents of the log area to a `.txt` file.

### 6.4. App Experience & UI Scaling

*   **Dynamic Layout:** The application window will support dynamic resizing.
*   **Element Behavior:** When the window is resized, the log/status area will be the primary element that expands to fill the new available space. The control/options panel may adjust its size slightly to maintain a balanced and professional appearance.