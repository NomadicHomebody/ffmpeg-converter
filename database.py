import sqlite3
from pathlib import Path
import json
import uuid
from datetime import datetime, timezone

from schemas import Job, JobStatus

# Define the path for the database in a 'data' subdirectory
DB_PATH = Path("data")
DB_FILE = DB_PATH / "jobs.db"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Initializes the database and creates the jobs table if it doesn't exist."""
    # Create the data directory if it doesn't exist
    DB_PATH.mkdir(exist_ok=True)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Create the jobs table
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
    conn.close()

def create_job(conn: sqlite3.Connection, job_id: uuid.UUID, correlation_id: str) -> Job:
    """Creates a new job record in the database."""
    cursor = conn.cursor()

    now = datetime.now(timezone.utc)
    job = Job(
        id=job_id,
        correlation_id=correlation_id,
        status=JobStatus.PENDING,
        progress=0.0,
        logs=[f"Job created at {now.isoformat()}"],
        result=None,
        created_at=now,
        updated_at=now,
    )

    cursor.execute("""
        INSERT INTO jobs (id, correlation_id, status, progress, logs, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (str(job.id), job.correlation_id, job.status.value, job.progress, json.dumps(job.logs), job.created_at.isoformat(), job.updated_at.isoformat()))

    conn.commit()
    return job

def get_job(conn: sqlite3.Connection, job_id: uuid.UUID) -> Job | None:
    """Retrieves a job record from the database."""
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM jobs WHERE id = ?", (str(job_id),))
    row = cursor.fetchone()

    if row is None:
        return None

    return Job(
        id=uuid.UUID(row["id"]),
        correlation_id=row["correlation_id"],
        status=JobStatus(row["status"]),
        progress=row["progress"],
        logs=json.loads(row["logs"]) if row["logs"] else [],
        result=json.loads(row["result"]) if row["result"] else None,
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )

def update_job_status(conn: sqlite3.Connection, job_id: uuid.UUID, status: JobStatus):
    """Updates the status of a job."""
    cursor = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute("UPDATE jobs SET status = ?, updated_at = ? WHERE id = ?", (status.value, now_iso, str(job_id)))
    conn.commit()

def log_to_job(conn: sqlite3.Connection, job_id: uuid.UUID, message: str):
    """Appends a log message to a job's log record."""
    cursor = conn.cursor()

    # This is not perfectly atomic but sufficient for this project's scale
    cursor.execute("SELECT logs FROM jobs WHERE id = ?", (str(job_id),))
    row = cursor.fetchone()
    if row is None:
        return

    logs = json.loads(row["logs"]) if row["logs"] else []
    logs.append(message)

    now_iso = datetime.now(timezone.utc).isoformat()
    cursor.execute("UPDATE jobs SET logs = ?, updated_at = ? WHERE id = ?", (json.dumps(logs), now_iso, str(job_id)))
    conn.commit()

