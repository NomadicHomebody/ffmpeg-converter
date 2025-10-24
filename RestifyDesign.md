# REST API Design for FFMPEG Bulk Converter

## 1. Project Goal

To extend the existing `ffmpeg-converter` application by adding a RESTful API interface. This will enable programmatic control over video conversions, allowing for integration with other services and automated workflows. The API will be containerized using Docker for easy deployment and scalability.

## 2. High-Level Architecture

We will introduce a new entry point for the application, a REST API built with **FastAPI**. The core conversion logic, currently present in `conversion_logic.py`, will be leveraged to perform the conversions. The existing GUI application (`converter_app.py`) will remain functional for local use.

### Proposed File Structure:

```
ffmpeg-converter/
├── api.py                  # New FastAPI application
├── conversion_logic.py     # Existing core logic (may require minor refactoring)
├── converter_app.py        # Existing GUI application
├── Dockerfile              # New Dockerfile for the API
├── docker-compose.yml      # New Docker Compose for easy startup
├── requirements.txt        # Updated with API dependencies
└── ...                     # Existing files
```

### Technology Choices:

*   **API Framework:** **FastAPI** - Chosen for its high performance, automatic interactive documentation (via Swagger UI), and modern Python features.
*   **Web Server:** **Uvicorn** - A lightning-fast ASGI server, required to run FastAPI.
*   **Containerization:** **Docker** - To create a portable and reproducible environment for the API.

## 3. API Endpoint Definition

We will expose a single primary endpoint to initiate the conversion process.

### `POST /convert`

This endpoint will initiate the bulk conversion process as a background task. To handle long-running conversions without timing out, the API will immediately accept the request and provide a job ID to track the progress.

We will use FastAPI's built-in `BackgroundTasks` feature to run the conversion process in the background. This avoids the complexity of a full message queue system like Celery for this stage of the project.

#### Request Body:

The request body will be a JSON object containing the conversion parameters, mirroring the options available in the GUI.

```json
{
  "input_directory": "/videos/input",
  "output_directory": "/videos/output",
  "video_codec": "hevc_nvenc",
  "audio_codec": "aac",
  "output_format": "mp4",
  "video_bitrate": "optimized",
  "bitrate_quality_profile": "Balanced Quality",
  "delete_input_files": false,
  "fallback_bitrate": "6M",
  "cap_dynamic_bitrate": true,
  "verbose_logging": false
}
```

#### Responses:

*   **`202 Accepted` - Conversion Started:**
    ```json
    {
      "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
      "status": "Conversion initiated.",
      "file_count": 5,
      "files_to_process": [
        "video1.mp4",
        "video2.mkv",
        "video3.mov",
        "video4.avi",
        "video5.wmv"
      ]
    }
    ```

*   **`400 Bad Request` - Invalid Input:**
    ```json
    {
      "error": "Invalid input directory provided: /videos/nonexistent"
    }
    ```

### `GET /status/{job_id}`

This endpoint allows clients to poll for the status of a conversion job.

#### Responses:

*   **`200 OK` - Status Retrieved:**
    *   **In Progress:**
        ```json
        {
          "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
          "status": "in_progress",
          "progress": {
            "completed_files": 2,
            "total_files": 5,
            "percentage": 40.0
          },
          "log": [
            "[14:32:10] Found 5 video files to convert.",
            "[14:32:12] Successfully converted video1.mp4.",
            "[14:32:15] Successfully converted video2.mkv."
          ]
        }
        ```
    *   **Completed:**
        ```json
        {
          "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
          "status": "completed",
          "message": "Conversion finished successfully.",
          "converted_files": [
            "/videos/output/z_video1.mp4",
            "/videos/output/z_video2.mkv",
            "/videos/output/z_video3.mov",
            "/videos/output/z_video4.avi",
            "/videos/output/z_video5.wmv"
          ],
          "log": [
            ...
          ]
        }
        ```
    *   **Failed:**
        ```json
        {
          "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
          "status": "failed",
          "error": "An error occurred during conversion of video3.mov.",
          "details": "ffmpeg error details..."
        }
        ```

*   **`404 Not Found` - Job Not Found:**
    ```json
    {
      "error": "Job ID not found."
    }
    ```

### `GET /health`

This endpoint performs a health check to verify that the API is running and that its critical dependency, `ffmpeg`, is installed and accessible.

#### Responses:

*   **`200 OK` - Healthy:**
    ```json
    {
      "status": "healthy",
      "ffmpeg_version": "ffmpeg version 4.4.2-0ubuntu0.22.04.1 Copyright (c) 2000-2021 the FFmpeg developers"
    }
    ```

*   **`503 Service Unavailable` - Unhealthy:**
    ```json
    {
      "status": "unhealthy",
      "error": "FFmpeg not found or not executable. Please check the installation."
    }
    ```

## 4. Core Logic Refactoring

The `conversion_logic.py` file will be adapted to support the asynchronous API.

1.  **Job Management:** We will implement a simple in-memory dictionary to store the state and results of each conversion job, keyed by `job_id`. This will be managed within `api.py`.
2.  **Background Task:** The main conversion loop (currently in `_conversion_worker` in the GUI app) will be refactored into a function that can be executed as a FastAPI `BackgroundTask`. This function will take the `job_id` and conversion parameters as arguments.
3.  **State Updates:** As the background task progresses, it will update the job's status (`in_progress`, `completed`, `failed`), progress percentage, and logs in the shared in-memory job store.
4.  **Decouple from GUI:** The core logic in `conversion_logic.py` will be fully decoupled from any GUI-specific code, such as Tkinter queues. It will be purely functional, receiving inputs and returning results or raising exceptions.

## 5. Configuration

Application behavior will be configured via environment variables, which can be set in the `docker-compose.yml` file.

*   `API_KEY`: (Optional) If set, enables API key authentication. Clients must provide this key in the `X-API-Key` header.
*   `MAX_CONCURRENT_JOBS`: (Default: `4`) An integer defining the maximum number of video files that can be processed concurrently across all jobs.

### Concurrency Control

The `POST /convert` endpoint will accept a `concurrent_conversions` parameter in its request body. The effective number of concurrent processes for a given job will be dynamically managed to respect the global `MAX_CONCURRENT_JOBS` limit.

The logic will be as follows:
1.  Check the number of currently active conversion processes.
2.  Calculate the available capacity: `available_capacity = MAX_CONCURRENT_JOBS - active_processes`.
3.  The number of workers for the new job will be: `min(requested_concurrency, available_capacity)`.
4.  If `available_capacity` is zero or less, the new job may be queued or rejected (TBD). For the initial design, we will prioritize throttling the request.

## 6. Job Persistence

To ensure job statuses persist across application restarts, we will use a simple, file-based SQLite database.

*   **Database File:** A single file, `jobs.db`, will be created in a persistent volume.
*   **Schema:** It will contain a `jobs` table to store job ID, status, progress, logs, and results.
*   **Benefit:** This approach is lightweight, requires no external database server, and is perfect for a self-contained, local application, as it's supported by Python's built-in `sqlite3` module.

## 7. Authentication

Authentication will be optional and based on a simple API key.

*   **Mechanism:** We will use FastAPI's `APIKeyHeader` security scheme.
*   **Usage:** If the `API_KEY` environment variable is set, the API will require clients to send a valid key in the `X-API-Key` HTTP header.
*   **Optional:** If the `API_KEY` environment variable is not set, authentication will be disabled, allowing for easy, unrestricted local use.

## 8. Dockerization Strategy

To support NVIDIA GPU acceleration (NVENC) for `ffmpeg` within a Python environment, we will use a specific Docker setup.

### `Dockerfile`

We will use a multi-stage build to create a clean and efficient final image:

1.  **Stage 1 (`builder`):** Use an image that contains a trusted, pre-compiled version of `ffmpeg` with NVENC support (e.g., `jrottenberg/ffmpeg:4.3-nvidia`).
2.  **Stage 2 (Final Image):**
    *   Start from an official NVIDIA CUDA base image that includes the necessary runtime libraries (e.g., `nvidia/cuda:11.8.0-runtime-ubuntu22.04`).
    *   Install Python 3.10 and pip.
    *   Copy the `ffmpeg` and `ffprobe` binaries from the `builder` stage.
    *   Copy the application code.
    *   Install Python dependencies from `requirements.txt`.
    *   This approach avoids a complex and slow `ffmpeg` compilation process while keeping the final image lean.

### `docker-compose.yml`

The `docker-compose.yml` will be updated to provide the container with access to the host's GPU.

```yaml
version: '3.8'
services:
  ffmpeg-converter-api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./videos:/videos
      - ./data:/app/data # Persistent volume for jobs.db
    environment:
      - API_KEY=your-secret-key # Optional: remove for no auth
      - MAX_CONCURRENT_JOBS=4
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

## 9. Requirements & Dependencies

The `requirements.txt` file will need to be updated with the following additions:

*   `fastapi`
*   `uvicorn`
*   `structlog`
*   `asgi-correlation-id`

## 10. Logging and Monitoring

To ensure the API is observable and easy to debug, we will implement standardized logging and tracing.

### Structured Logging

We will use the `structlog` library to enforce structured, JSON-formatted logging. This allows for easy parsing, filtering, and analysis by log management systems.

### Correlation ID for Traceability

To trace a request throughout its entire lifecycle, including background tasks, we will use the `asgi-correlation-id` middleware. 

*   It will automatically inject a unique `correlation_id` into every log record for a given request.
*   It will honor a `Client-Correlation-Id` header if provided by the client; otherwise, it will generate a new UUID for the request.
*   This ensures that all logs, from the initial request to the completion of the background conversion, can be tied together.

**Example Log Output:**
```json
{
    "level": "info",
    "event": "Conversion of video1.mp4 started.",
    "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "correlation_id": "Client-Provided-ID-12345", 
    "timestamp": "2025-10-23T14:32:11Z"
}
```

### Health Monitoring

The `GET /health` endpoint is designed for integration with uptime monitoring services like Uptime Kuma. By periodically making a request to this endpoint and asserting a `200 OK` status code, these tools can verify the health and availability of the API and its `ffmpeg` dependency.

