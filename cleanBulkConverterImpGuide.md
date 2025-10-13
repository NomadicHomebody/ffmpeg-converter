# FFMPEG Bulk Converter Implementation Guide

This guide provides a step-by-step checklist for implementing the FFMPEG Bulk Converter GUI tool.

## Phase 1: Core Logic & Backend

- [x] **Project Setup**
    - [x] Create a new Python file for the main application logic (e.g., `converter_app.py`).
    - [x] Create a separate module for the core conversion functions (e.g., `conversion_logic.py`).

- [x] **Conversion Logic (`conversion_logic.py`)**
    - [x] Create a function to scan a directory for video files (non-recursively).
    - [x] Create a function to construct the `ffmpeg` command string based on user selections (video codec, audio codec, format, bitrate).
    - [x] Implement the logic for the dynamic bitrate option (i.e., how to determine the bitrate of the input file).
    - [x] Create a function to execute the `ffmpeg` command using `subprocess`.
    - [x] Implement the output file naming logic:
        - [x] Prefix new files with "z_".
        - [x] If a conflict exists, use a numeric suffix (e.g., "z_1", "z_2").

- [x] **Initial Testing (Command-Line)**
    - [x] Temporarily add command-line argument parsing (`argparse`) to `converter_app.py` to test the core logic.
    - [x] Test the conversion process with various options.

## Phase 2: GUI Development (Tkinter)

- [x] **Main Window**
    - [x] Create the main Tkinter window.
    - [x] Set the window title and initial size.

- [x] **Widgets**
    - [x] Add a "Select Input Folder" button and a label to display the selected path.
    - [x] Add a "Select Output Folder" button and a label to display the selected path.
    - [x] Create and populate the dropdown menu for video codecs.
    - [x] Create and populate the dropdown menu for audio codecs.
    - [x] Create and populate the dropdown menu for file formats.
    - [x] Create and populate the dropdown menu for video bitrates (10-250Mbps + dynamic option).
    - [x] Add a "Start Conversion" button.
    - [x] Add a progress bar.
    - [x] Add a text area for logging and status updates.

- [x] **GUI Logic**
    - [x] Implement the functions that are called when the folder selection buttons are clicked.
    - [x] Write the function that is called when the "Start Conversion" button is clicked. This function will gather all the user's selections and call the core conversion logic.

## Phase 3: Concurrency & User Experience

- [x] **Threading**
    - [x] Modify the "Start Conversion" function to run the conversion process in a separate thread to keep the GUI responsive.
    - [x] Use a queue to safely pass messages (e.g., progress updates, log messages) from the conversion thread back to the main GUI thread.

- [x] **Progress & Logging**
    - [x] Update the GUI periodically to reflect the progress of the conversion (e.g., update the progress bar).
    - [x] Display log messages from the conversion thread in the text area.

- [x] **State Management**
    - [x] Disable the selection widgets and the "Start Conversion" button while a conversion is in progress.
    - [x] Add a "Cancel" button that becomes active during conversion.
    - [x] Implement the logic for the "Cancel" button to terminate the conversion thread.
    - [x] Re-enable the UI elements when the conversion is complete or canceled.

## Phase 4: Error Handling & Refinements

- [x] **FFmpeg Check**
    - [x] On startup, check if `ffmpeg` is installed and accessible in the system's PATH.
    - [x] If `ffmpeg` is not found, display an error message to the user.

- [x] **Error Handling**
    - [x] Wrap the `ffmpeg` execution in a `try...except` block.
    - [x] Catch any errors from the `subprocess` and display them in the log area.
    - [x] Add checks to ensure that the user has selected both an input and an output folder before starting the conversion.

## Phase 5: Delete Input File

- [x] **GUI Toggle**
    - [x] Add a checkbox/toggle switch to the GUI labeled "Delete input files after successful conversion".
- [x] **Deletion Logic**
    - [x] In the `_conversion_worker` method, after a successful conversion, check if the delete toggle is enabled.
    - [x] If enabled, use `os.remove()` to delete the original input file.
    - [x] Add a log message to indicate that the file has been deleted.

## Phase 6: Code Enhancements

- [x] **Dynamic Bitrate Fallback**
    - [x] Add a new entry field to the GUI for a fallback bitrate.
    - [x] In `conversion_logic.py`, when "dynamic" bitrate is selected and `get_video_bitrate` returns `None`, use the fallback bitrate.
- [x] **Clear Log Button**
    - [x] Add a "Clear Log" button to the GUI.
    - [x] Implement the logic for the "Clear Log" button to clear the log area.
- [x] **Enhanced Cancel Logic**
    - [x] In `conversion_logic.py`, modify `execute_ffmpeg_command` to store the `subprocess` Popen object.
    - [x] In `converter_app.py`, when the "Cancel" button is clicked, in addition to setting the event, call a new method to terminate the `ffmpeg` process directly.

## Phase 7: Packaging & Distribution

- [ ] **PyInstaller Setup**
    - [ ] Install PyInstaller (`pip install pyinstaller`).
    - [ ] Create a `.spec` file for PyInstaller to configure the build.

- [ ] **Build Executable**
    - [ ] Run PyInstaller to package the application into a single `.exe` file.
    - [ ] Test the executable on a clean Windows environment.

- [ ] **Documentation**
    - [ ] Create a `README.md` file with:
        - [ ] A description of the tool.
        - [ ] Instructions for how to build a fresh `.exe` after updating code
        - [ ] Instructions on how to use it.
        - [ ] A clear statement that `ffmpeg` must be installed separately. (Include link to ffmpeg install instrucions webpage)
