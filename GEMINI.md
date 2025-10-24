# Project: FFMPEG Bulk Converter (GUI & REST API)

## Project Overview

This project provides a Python-based tool for bulk video conversion using `ffmpeg`. It exists as two primary interfaces:

1.  A **Tkinter-based GUI application** for interactive, local conversions.
2.  A **Dockerized REST API** built with FastAPI for programmatic and automated conversion workflows.

The project is currently entering a new phase to build out the REST API functionality as detailed in `RestifyDesign.md` and `RestifyImplementationPlan.md`.

**Key Technologies:**
*   **Language:** Python
*   **GUI Framework:** Tkinter
*   **API Framework:** FastAPI
*   **Database:** SQLite (for job persistence)
*   **Containerization:** Docker
*   **Testing:** pytest
*   **Packaging:** PyInstaller (for the GUI version)

**Architecture:**
The application is designed with a separation of concerns:
*   `converter_app.py`: Main application entry point and GUI logic.
*   `api.py`: The new REST API entry point using FastAPI.
*   `conversion_logic.py`: Core business logic for handling `ffmpeg` conversions, shared by both the GUI and the API.
*   `database.py`: Manages the SQLite database for API job persistence.

## Building and Running

### GUI Application
**1. Setup:**
Install the required Python dependencies.
```bash
pip install -r requirements.txt
```

**2. Running the Application:**
```bash
python converter_app.py
```

### REST API (Docker)
**1. Setup:**
Ensure you have Docker and Docker Compose installed, along with an NVIDIA GPU and the NVIDIA Container Toolkit for hardware acceleration.

**2. Running the API:**
```bash
docker-compose up --build
```
The API will be available at `http://localhost:8000`.

## Development Cycle

Our development process will now be guided by the **`RestifyImplementationPlan.md`** file. I will work through the checklist in this implementation plan, one phase at a time.

For each major phase or task, I will:
1.  State the goal of the step I am about to perform.
2.  Implement the required functionality and associated tests.
3.  Mark the task as complete in `RestifyImplementationPlan.md`.
4.  Provide a summary of the changes made.
5.  Ask for your approval before proceeding to the next task.