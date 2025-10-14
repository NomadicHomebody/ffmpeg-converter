# Project: FFMPEG Bulk Converter GUI

## Project Overview

This project aims to build a Python-based GUI tool for bulk video conversion using the `ffmpeg` command-line tool. The application will allow users to select a folder of videos and convert them to a specified format, codec, and bitrate.

The project is currently in an advanced development phase, following a detailed plan outlined in `cleanBulkConverterPlan.md` and `cleanBulkConverterImpGuide.md`.

**Key Technologies:**
*   **Language:** Python
*   **GUI Framework:** Tkinter
*   **Testing:** pytest
*   **Packaging:** PyInstaller

**Architecture:**
The application is designed with a separation of concerns:
*   **`converter_app.py`**: Main application entry point and GUI logic.
*   **`conversion_logic.py`**: Core business logic for handling `ffmpeg` conversions.

## Building and Running

**1. Setup:**
Install the required Python dependencies.
```bash
pip install -r requirements.txt
```

**2. Running the Application:**
```bash
python converter_app.py
```

## Development Conventions

*   **Workflow:** The project follows a structured development process, starting with planning (`.md` files) before implementation.
*   **Code Style:** Follow standard Python conventions (PEP 8).
*   **File Naming:** Converted files will be prefixed with `z_` and handle naming conflicts with numeric suffixes, as specified in the implementation plan.

## Development Cycle

Our development process will be guided by the `cleanBulkConverterImpGuide.md` file. I will work through the checklist in the implementation guide, one task at a time. The project is in the final stages of implementation.

For each task, I will:
1.  Implement the required functionality.
2.  Create or update tests to validate the implementation.
3.  Mark the task as complete in `cleanBulkConverterImpGuide.md`.
4.  Provide a summary of the changes made.
5.  Ask for your approval before proceeding to the next task.