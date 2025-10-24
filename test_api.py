import pytest
from fastapi.testclient import TestClient
import uuid
import sqlite3

from api import app, get_db
from config import settings

# Override the database dependency to use an in-memory SQLite database for tests
@pytest.fixture
def override_get_db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Use the schema from database.py to create the table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        correlation_id TEXT,
        status TEXT NOT NULL,
        progress REAL NOT NULL,
        logs TEXT,
        result TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    conn.commit()

    def _override_get_db():
        try:
            yield conn
        finally:
            pass # Keep connection open for the duration of the test
    
    return _override_get_db

@pytest.fixture
def client(override_get_db, monkeypatch):
    # Disable API key for most tests
    monkeypatch.setattr(settings, "API_KEY", None)

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# --- Test Cases ---

def test_read_root(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the FFMPEG Bulk Converter API"}

def test_health_check_success(client, monkeypatch):
    """Test the health check when ffmpeg is found."""
    # Mock subprocess.run to simulate success
    class MockCompletedProcess:
        stdout = "ffmpeg version 4.4.2-0ubuntu0.22.04.1 Copyright (c) 2000-2021 the FFmpeg developers\nmore text"
        def check_returncode(self): pass

    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: MockCompletedProcess())
    
    response = client.get("/health")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "healthy"
    assert "ffmpeg version" in json_response["ffmpeg_version"]

def test_health_check_fail(client, monkeypatch):
    """Test the health check when ffmpeg is not found."""
    # Mock subprocess.run to simulate FileNotFoundError
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: exec("raise FileNotFoundError"))

    response = client.get("/health")
    assert response.status_code == 503
    assert response.json()["detail"]["status"] == "unhealthy"

def test_create_job_and_get_status(client, monkeypatch, tmp_path):
    """Test creating a job and then polling its status."""
    # Mock the background task so it doesn't actually run ffmpeg
    monkeypatch.setattr("api.run_api_conversion_job", lambda *args, **kwargs: None)
    
    # Create a dummy input directory and a file
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "test.mp4").touch()

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # --- Create Job ---
    request_body = {
        "input_directory": str(input_dir),
        "output_directory": str(output_dir)
    }
    response = client.post("/convert", json=request_body)
    
    assert response.status_code == 202
    json_response = response.json()
    assert "job_id" in json_response
    assert json_response["status"] == "Conversion initiated."
    assert json_response["file_count"] == 1
    assert json_response["files_to_process"] == ["test.mp4"]
    
    job_id = json_response["job_id"]

    # --- Get Status ---
    response = client.get(f"/status/{job_id}")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["id"] == job_id
    assert json_response["status"] == "pending"

def test_get_status_not_found(client):
    """Test getting the status of a non-existent job."""
    non_existent_id = uuid.uuid4()
    response = client.get(f"/status/{non_existent_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Job not found"}

def test_create_job_no_videos_found(client, tmp_path):
    """Test creating a job where the input directory is empty."""
    input_dir = tmp_path / "empty_input"
    input_dir.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    request_body = {
        "input_directory": str(input_dir),
        "output_directory": str(output_dir)
    }
    response = client.post("/convert", json=request_body)
    assert response.status_code == 404
    assert "No video files found" in response.json()["detail"]


def test_api_key_auth(client, monkeypatch, tmp_path):
    """Test the API key authentication flow."""
    # --- Setup for auth test ---
    monkeypatch.setattr(settings, "API_KEY", "test-key-123")
    monkeypatch.setattr("api.run_api_conversion_job", lambda *args, **kwargs: None)

    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "test.mp4").touch()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    request_body = {"input_directory": str(input_dir), "output_directory": str(output_dir)}

    # 1. No API Key -> Fail
    response = client.post("/convert", json=request_body)
    assert response.status_code == 401
    assert response.json() == {"detail": "API Key required."}

    # 2. Wrong API Key -> Fail
    response = client.post("/convert", json=request_body, headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid API Key."}

    # 3. Correct API Key -> Success
    response = client.post("/convert", json=request_body, headers={"X-API-Key": "test-key-123"})
    assert response.status_code == 202

    # 4. Health endpoint should still be public
    # We need to mock subprocess again for this client
    class MockCompletedProcess:
        stdout = "ffmpeg version 4.4.2"
        def check_returncode(self): pass
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: MockCompletedProcess())
    response = client.get("/health")
    assert response.status_code == 200
