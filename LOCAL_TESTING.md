# Local API Testing Guide

This guide provides instructions on how to set up and run the FFMPEG Converter REST API on your local machine for development and testing purposes, without using Docker.

## 1. Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.10+**
- **FFmpeg:** It must be installed and accessible from your system's PATH. You can verify this by running `ffmpeg -version` in your terminal.

## 2. Setup Instructions

Follow these steps to set up your local development environment.

### Step 2.1: Create and Activate a Virtual Environment

From the project's root directory, create a new Python virtual environment. This keeps your project dependencies isolated.

```bash
# Create the virtual environment
python -m venv .venv
```

Next, activate it.

**On Windows:**
```bash
.venv\Scripts\activate
```

**On macOS / Linux:**
```bash
source .venv/bin/activate
```

Your terminal prompt should now indicate that you are in the `.venv` environment.

### Step 2.2: Install Dependencies

Install all the required Python packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### Step 2.3: Configure Environment Variables

The application is configured using a `.env` file. We have already created this file. For local testing, you can set the following variables inside it:

```dotenv
# .env file

# The API key for authentication. If left empty or commented out, auth is disabled.
API_KEY=your-secret-key-here

# The maximum number of concurrent FFMPEG processes allowed.
MAX_CONCURRENT_JOBS=4
```

## 3. Running the Local Server

Once the setup is complete, you can run the API using the Uvicorn development server.

```bash
uvicorn api:app --reload
```

- `api:app`: Tells Uvicorn to find the `app` object inside the `api.py` file.
- `--reload`: Enables hot-reloading, so the server will automatically restart when you save changes to the code.

The server will start and be accessible at **`http://127.0.0.1:8000`**.

## 4. Testing the API

You can interact with your local API in several ways:

### Interactive Docs (Swagger UI)

FastAPI provides automatic interactive documentation. Once the server is running, open your web browser and navigate to:

**`http://127.0.0.1:8000/docs`**

Here you can see all available endpoints, view their models, and even send test requests directly from your browser.

### Using `curl`

You can use a command-line tool like `curl` to test the endpoints. For example, to test the `/health` endpoint:

```bash
curl http://127.0.0.1:8000/health
```

You should see a JSON response indicating a `healthy` status and the FFmpeg version.
