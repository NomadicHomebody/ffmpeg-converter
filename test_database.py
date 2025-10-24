import pytest
import sqlite3
import uuid
from datetime import datetime, timezone

from schemas import JobStatus
import database

@pytest.fixture
def test_db(monkeypatch):
    """Fixture to set up an in-memory SQLite database for testing."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    
    # Monkeypatch the get_db_connection to return our in-memory connection
    monkeypatch.setattr(database, 'get_db_connection', lambda: conn)
    
    # Manually initialize the schema in the in-memory database
    cursor = conn.cursor()
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
    
    yield conn
    
    conn.close()

def test_initialize_database(test_db):
    """Test that the jobs table is created correctly."""
    cursor = test_db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs';")
    assert cursor.fetchone() is not None, "The 'jobs' table should be created."

def test_create_and_get_job(test_db):
    """Test creating a new job and then retrieving it."""
    # Happy Path for create_job and get_job
    job_id = uuid.uuid4()
    correlation_id = "test-corr-id-123"
    
    created_job = database.create_job(test_db, job_id, correlation_id)
    
    assert created_job.id == job_id
    assert created_job.correlation_id == correlation_id
    assert created_job.status == JobStatus.PENDING
    assert created_job.progress == 0.0
    assert len(created_job.logs) == 1

    # Retrieve the job and verify
    retrieved_job = database.get_job(test_db, job_id)
    
    assert retrieved_job is not None
    assert retrieved_job.id == job_id
    assert retrieved_job.correlation_id == correlation_id
    assert retrieved_job.status == JobStatus.PENDING
    assert retrieved_job.created_at == created_job.created_at

def test_get_job_not_found(test_db):
    """Test that get_job returns None for a non-existent job."""
    # Edge Case: Job not found
    non_existent_id = uuid.uuid4()
    retrieved_job = database.get_job(test_db, non_existent_id)
    assert retrieved_job is None

def test_update_job_status(test_db):
    """Test updating a job's status."""
    job_id = uuid.uuid4()
    correlation_id = "test-update-status"
    
    original_job = database.create_job(test_db, job_id, correlation_id)
    original_updated_at = original_job.updated_at

    # Update status
    database.update_job_status(test_db, job_id, JobStatus.IN_PROGRESS)
    
    updated_job = database.get_job(test_db, job_id)
    
    assert updated_job is not None
    assert updated_job.status == JobStatus.IN_PROGRESS
    # Check that the updated_at timestamp has changed
    assert updated_job.updated_at > original_updated_at

def test_log_to_job(test_db):
    """Test appending log messages to a job."""
    job_id = uuid.uuid4()
    correlation_id = "test-logging"
    
    database.create_job(test_db, job_id, correlation_id)
    
    # Log multiple messages
    log_message_1 = "Conversion started."
    log_message_2 = "Processing file 1 of 10."
    database.log_to_job(test_db, job_id, log_message_1)
    database.log_to_job(test_db, job_id, log_message_2)
    
    retrieved_job = database.get_job(test_db, job_id)
    
    assert retrieved_job is not None
    # The first log is the creation message
    assert len(retrieved_job.logs) == 3 
    assert retrieved_job.logs[1] == log_message_1
    assert retrieved_job.logs[2] == log_message_2

def test_log_to_job_non_existent(test_db):
    """Test that logging to a non-existent job does not raise an error."""
    # Edge Case: Logging to a job that doesn't exist
    try:
        database.log_to_job(test_db, uuid.uuid4(), "This should not crash.")
    except Exception as e:
        pytest.fail(f"log_to_job raised an unexpected exception: {e}")
