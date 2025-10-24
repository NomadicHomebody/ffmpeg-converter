# FFMPEG Converter - REST API Implementation Plan

This document outlines the step-by-step plan to implement the REST API, containerize it with Docker, and create the necessary documentation.

## Phase 1: Project Setup & Prerequisites

- [x] **1.1: Update Dependencies**
  - [x] Add `fastapi`, `uvicorn[standard]`, `structlog`, `asgi-correlation-id`, `pydantic-settings`, and `aiofiles` to `requirements.txt`.

- [x] **1.2: Create New Project Files**
  - [x] Create `api.py` for the FastAPI application.
  - [x] Create `Dockerfile` for containerization.
  - [x] Create `docker-compose.yml` for service orchestration.
  - [x] Create `.env` file for local environment variables and add it to `.gitignore`.
  - [x] Create `database.py` for SQLite database logic.
  - [x] Create `schemas.py` for Pydantic models.
  - [x] Create `config.py` for application settings management.

- [x] **1.3: Set Up Local Environment**
  - [x] Create and activate a new Python virtual environment.
  - [x] Install the updated dependencies: `pip install -r requirements.txt`.

## Phase 2: Core API Scaffolding & Configuration

- [x] **2.1: Implement Basic FastAPI App**
  - [x] In `api.py`, initialize the FastAPI application.
  - [x] Add a root `GET /` endpoint that returns a welcome message.

- [x] **2.2: Implement Logging & Correlation ID**
  - [x] In a new `logging_config.py`, configure `structlog` for JSON output.
  - [x] In `api.py`, add the `asgi-correlation-id` middleware.
  - [x] Ensure logs include the correlation ID.

- [x] **2.3: Implement Configuration Management**
  - [x] In `config.py`, create a Pydantic `Settings` class to load `API_KEY` and `MAX_CONCURRENT_JOBS` from environment variables.

- [x] **2.4: Implement Health Check Endpoint**
  - [x] In `api.py`, create the `GET /health` endpoint.
  - [x] The endpoint should run `ffmpeg -version` and return the version string in the response.
  - [x] It should return a `200 OK` on success and `503 Service Unavailable` on failure.
  - [x] **Test:** Manually test the endpoint to confirm it works as expected.

## Phase 3: Job Persistence with SQLite

- [x] **3.1: Define Database Schema and Models**
  - [x] In `database.py`, write a function to initialize the SQLite database and create a `jobs` table. The table should store `job_id`, `status`, `progress`, `logs`, `result`, `created_at`, etc.
  - [x] In `schemas.py`, create Pydantic models for `JobCreate`, `Job`, etc.

- [x] **3.2: Create Database Utility Functions**
  - [x] In `database.py`, create CRUD functions:
    - `create_job(...)`
    - `get_job(job_id)`
    - `update_job_status(job_id, status)`
    - `update_job_progress(job_id, progress)`
    - `log_to_job(job_id, message)`

- [x] **3.3: Write Database Tests**
  - [x] Create a new `test_database.py` file.
  - [x] Write `pytest` unit tests for all CRUD functions to ensure they work correctly.

## Phase 4: API Endpoint Implementation & Logic

- [ ] **4.1: Refactor `conversion_logic.py` for API Support**
  - [ ] **CRITICAL:** All changes must be backward-compatible. The existing GUI application (`converter_app.py`) must continue to function without any modification.
  - [ ] Create a new, separate worker function (e.g., `run_api_conversion_job`) that orchestrates the conversion process specifically for the API.
  - [ ] This new function will use the database utility functions (`update_job_status`, `log_to_job`) for state management.
  - [ ] The existing functions used by the GUI worker will not be modified in a breaking way. Core, stateless utility functions (e.g., `build_ffmpeg_command`) will be shared.

- [ ] **4.2: Implement `POST /convert` Endpoint**
  - [ ] In `api.py`, create the endpoint.
  - [ ] Use Pydantic models from `schemas.py` for request body validation.
  - [ ] Implement the concurrency control logic defined in the design document.
  - [ ] Create a job record in the database.
  - [ ] Use FastAPI's `BackgroundTasks` to run the `run_conversion_task` function in the background.
  - [ ] Return a `202 Accepted` response with the job details.

- [ ] **4.3: Implement `GET /status/{job_id}` Endpoint**
  - [ ] In `api.py`, create the endpoint.
  - [ ] Fetch the job status from the SQLite database using `get_job`.
  - [ ] Return the job details in the response, or a `404 Not Found` if the job doesn't exist.

- [ ] **4.4: Implement Optional API Key Authentication**
  - [ ] In a new `security.py` file, create a dependency that checks for the `X-API-Key` header against the `API_KEY` from settings.
  - [ ] The dependency should be optional, disabling auth if `API_KEY` is not set.
  - [ ] Apply this dependency to the `/convert` and `/status` endpoints.

- [ ] **4.5: Write API Integration Tests**
  - [ ] Create a new `test_api.py` file.
  - [ ] Write integration tests that:
    - Call `POST /convert` and verify the response.
    - Call `GET /status/{job_id}` to check for `in_progress` status.
    - (Mock the conversion task) Check for `completed` status.
    - Test the authentication (with and without a key).
    - Test the `/health` endpoint.

## Phase 5: Dockerization & Deployment

- [ ] **5.1: Create Multi-Stage `Dockerfile`**
  - [ ] Implement the multi-stage build as designed in `RestifyDesign.md`.
  - [ ] Ensure `ffmpeg` with NVENC support is correctly copied to the final image.
  - [ ] Ensure Python dependencies are installed.

- [ ] **5.2: Create `docker-compose.yml`**
  - [ ] Implement the `docker-compose.yml` file as designed.
  - [ ] Include the `deploy` key for GPU access.
  - [ ] Set up volumes for `/videos` and the SQLite database file.
  - [ ] Pass environment variables for `API_KEY` and `MAX_CONCURRENT_JOBS`.

- [ ] **5.3: Build and Test the Container**
  - [ ] Run `docker-compose build` to build the image.
  - [ ] Run `docker-compose up` to start the service.
  - [ ] Test the running container by sending requests to the API (e.g., using `curl` or Postman).
  - [ ] Verify that a conversion job runs and utilizes the GPU (check `nvidia-smi` on the host).

## Phase 6: Documentation & Deliverables

- [ ] **6.1: Update Project `README.md`**
  - [ ] Add a new section for the REST API.
  - [ ] Include a brief overview and link to the detailed API documentation.

- [ ] **6.2: Create `API_DOCUMENTATION.md`**
  - [ ] Create a comprehensive guide that includes:
    - **Local Setup:** How to run the API locally without Docker.
    - **Docker Deployment:** How to build and run the application with `docker-compose`.
    - **Configuration:** How to set environment variables (`API_KEY`, `MAX_CONCURRENT_JOBS`).
    - **API Usage:** Detailed explanation of each endpoint with `curl` examples.

- [ ] **6.3: Generate Postman Collection**
  - [ ] Create a JSON file named `postman_collection.json`.
  - [ ] Add requests for `GET /health`, `POST /convert`, and `GET /status/{job_id}`.
  - [ ] Pre-fill the request body for `/convert` and include the `X-API-Key` header.
  - [ ] Add this file to the repository.

- [ ] **6.4: Verify Swagger UI Documentation**
  - [ ] Run the application and navigate to `/docs`.
  - [ ] Review the auto-generated Swagger UI documentation.
  - [ ] Ensure all endpoints, models, and parameters are correctly documented. Add descriptions and examples in the FastAPI code where needed.
