# Enhanced Progress Window Implementation Plan

This document provides a detailed, step-by-step guide for implementing a standalone GUI progress window for the MKV to MP4 bulk converter.

## 1. Feature Overview

The goal is to create a separate window that displays the progress of the conversion process, including a progress bar, percentage complete, status message, and estimated time remaining. This window will run in a separate process and receive updates from the main conversion script via a TCP socket.

## 2. Step-by-Step Implementation

### Step 1: Update Dependencies

Add `PySide6` to the `requirements.txt` file. This library is required for the GUI window.

**File: `requirements.txt`**
```
# Python 3.8+ required
click==8.2.2
structlog==24.1.0
tqdm==4.67.1
PySide6==6.8.1
```

### Step 2: Create the Progress Window GUI

Create a new file named `progress_window.py`. This script will contain the code for the GUI window, which acts as a socket client.

**File: `progress_window.py`**
```python
"""
Standalone Progress Window for Bulk MKV to MP4 Converter

Implements a PySide6 GUI window that receives progress updates via TCP/IP socket.
"""
import sys
import json
import socket
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QProgressBar, QLabel
from PySide6.QtCore import QTimer, Qt

class ProgressWindow(QMainWindow):
    def __init__(self, host='127.0.0.1', port=56789):
        super().__init__()
        self.setWindowTitle("Bulk Conversion Progress")
        self.setGeometry(100, 100, 400, 120)

        # --- UI Elements ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.percent_label = QLabel("0.0% Complete")
        self.status_label = QLabel("Waiting for updates...")
        self.remaining_label = QLabel("Estimated Time Remaining: --:--:--")

        # --- Layout ---
        layout = QVBoxLayout()
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.percent_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.remaining_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # --- Socket Client Setup ---
        self.host = host
        self.port = port
        self.sock = None
        self.connect_socket()

        # --- Timer to Poll for Updates ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.poll_socket)
        self.timer.start(200) # Poll every 200ms

    def connect_socket(self):
        """Initializes the socket connection to the server."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.sock.setblocking(False) # Use non-blocking socket
            self.status_label.setText("Connected to server.")
        except Exception as e:
            self.status_label.setText(f"Connection failed: {e}")
            self.sock = None

    def poll_socket(self):
        """Polls the socket for new data and updates the GUI."""
        if not self.sock:
            return

        try:
            data = self.sock.recv(4096)
            if not data:
                return # Connection closed by server

            # Process all messages in the buffer
            for line in data.decode('utf-8').strip().splitlines():
                try:
                    update = json.loads(line)
                    self.update_progress(update)
                except json.JSONDecodeError:
                    # Ignore malformed JSON
                    continue
        except BlockingIOError:
            # No data available right now
            pass
        except Exception as e:
            self.status_label.setText(f"Socket error: {e}")

    def update_progress(self, update: dict):
        """Updates the progress bar and labels with new data."""
        percent = update.get("percent", 0.0)
        status = update.get("status", "")
        remaining = update.get("remaining_time", "--:--:--")

        self.progress_bar.setValue(int(percent))
        self.percent_label.setText(f"{percent:.1f}% Complete")
        self.status_label.setText(status)
        self.remaining_label.setText(f"Estimated Time Remaining: {remaining}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProgressWindow()
    window.show()
    sys.exit(app.exec())
```

### Step 3: Modify the Main Converter Script

Update `mkv_mp4_bulk_converter.py` to act as a socket server and send progress updates.

#### 3.1 Add `--progress-window` CLI Option

Add a new `click.option` to enable the GUI progress window feature.

**File: `mkv_mp4_bulk_converter.py`**
```python
# ... (imports)

# ... (other code)

@click.option(
    "--progress-window",
    is_flag=True,
    default=False,
    help="Show standalone GUI progress window."
)
def main(
    input_folder: str,
    dry_run: bool,
    verbose: bool,
    progress: bool,
    progress_window: bool
) -> None:
    # ...
```

#### 3.2 Implement Socket Server and IPC Logic

In the `main` function, add the server-side socket logic. This will only run if the `--progress-window` flag is used.

**File: `mkv_mp4_bulk_converter.py`**
```python
# ... (imports)
import socket
import json

# ... (main function signature)
def main(
    input_folder: str,
    dry_run: bool,
    verbose: bool,
    progress: bool,
    progress_window: bool
) -> None:
    """Entry point for the bulk MKV to MP4 converter CLI."""

    import subprocess

    logger.info("About to call find_mkv_files", input_folder=input_folder)
    mkv_files: list[str] = find_mkv_files(input_folder)
    if not mkv_files:
        logger.warning("No .mkv files found in the specified folder.", input_folder=input_folder)
        return

    # --- IPC server setup for progress window ---
    client_conn = None
    if progress_window:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as progress_sock:
                progress_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                progress_sock.bind(("127.0.0.1", 56789))
                progress_sock.listen(1)
                logger.info("Waiting for progress window to connect...")
                progress_sock.settimeout(10) # 10-second timeout
                try:
                    client_conn, _ = progress_sock.accept()
                    client_conn.settimeout(0.1) # Non-blocking send
                    logger.info("Progress window connected.")
                except socket.timeout:
                    logger.warning("No progress window connected after 10 seconds.")
                    client_conn = None
        except Exception as e:
            logger.error("Failed to set up progress window socket.", error=str(e))
            client_conn = None


    # ... (tqdm setup)

    for idx, mkv_path in enumerate(file_iter, 1):
        mp4_path = mkv_path[:-4] + "_.mp4"
        cmd = build_ffmpeg_command(mkv_path, mp4_path)
        percent = (idx / len(mkv_files)) * 100

        # ... (tqdm postfix update)
        
        status_msg = f"[{idx}/{len(mkv_files)}] {os.path.basename(mkv_path)}"

        # --- Send progress update to GUI window ---
        if client_conn:
            try:
                update = {
                    "percent": percent,
                    "status": status_msg,
                    "remaining_time": remaining_time # From tqdm
                }
                # Send data as a newline-terminated JSON string
                client_conn.sendall((json.dumps(update) + '''
''').encode("utf-8"))
            except (socket.error, BrokenPipeError) as e:
                logger.warning("Failed to send progress update to window. Connection may be closed.", error=str(e))
                client_conn = None # Stop trying to send

        # ... (subprocess execution and file removal)

    # --- Final update and cleanup ---
    if client_conn:
        final_update = {
            "percent": 100,
            "status": "Conversion complete.",
            "remaining_time": "00:00:00"
        }
        client_conn.sendall((json.dumps(final_update) + '''
''').encode("utf-8"))
        client_conn.close()
```

### Step 4: Running and Testing

1.  **Start the GUI:**
    Open a terminal and run:
    ```bash
    python progress_window.py
    ```
    The progress window should appear and display "Waiting for updates..." or "Connected to server."

2.  **Start the Conversion:**
    Open a second terminal and run the main script with the `--progress-window` flag:
    ```bash
    python mkv_mp4_bulk_converter.py /path/to/your/videos --progress-window
    ```

3.  **Verify:**
    The progress window should update in real-time as the conversion script processes the files.

#### Specific Test Case

To ensure robust handling of paths with spaces and special characters, test with the following specific folder path:

```bash
python mkv_mp4_bulk_converter.py "D:\Library\JellyFin\Films\The Fantastic 4 - First Steps (2025)" --progress-window
```
**Expected Outcome:** The script should correctly identify and convert video files within this directory without errors related to the path.
