import sqlite3
from pathlib import Path
import json

# Define the path for the database in a 'data' subdirectory
DB_PATH = Path("data")
DB_FILE = DB_PATH / "jobs.db"

def initialize_database():
    """Initializes the database and creates the jobs table if it doesn't exist."""
    # Create the data directory if it doesn't exist
    DB_PATH.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_FILE)
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
