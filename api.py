from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.context import correlation_id
import structlog
import subprocess
import uuid
import sqlite3
from pathlib import Path

from logging_config import configure_logging
import database
import schemas
from conversion_logic import run_api_conversion_job, find_video_files

# Configure logging and initialize database before starting the app
configure_logging()
database.initialize_database()

app = FastAPI(
    title="FFMPEG Bulk Converter API",
    description="An API for bulk video conversion using FFMPEG.",
    version="1.0.0",
)

app.add_middleware(CorrelationIdMiddleware)

log = structlog.get_logger()

# Dependency to get a DB connection
def get_db():
    db = database.get_db_connection()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    """A welcome message for the API root."""
    log.info("Root endpoint was hit")
    return {"message": "Welcome to the FFMPEG Bulk Converter API"}


@app.post("/convert", status_code=202, tags=["Conversion"])
def create_conversion_job(
    request: schemas.ConversionRequest,
    background_tasks: BackgroundTasks,
    db: sqlite3.Connection = Depends(get_db)
):
    """Initiates a new video conversion job."""
    job_id = uuid.uuid4()
    corr_id = correlation_id.get()
    log.info("Received conversion request", body=request.model_dump(), job_id=str(job_id))

    try:
        video_files = find_video_files(request.input_directory)
        if not video_files:
            raise HTTPException(status_code=404, detail=f"No video files found in directory: {request.input_directory}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Create the job record in the database
    job = database.create_job(db, job_id, corr_id)

    # Add the conversion process to run in the background
    background_tasks.add_task(
        run_api_conversion_job,
        job_id=job_id,
        input_dir=request.input_directory,
        output_dir=request.output_directory,
        video_codec=request.video_codec,
        audio_codec=request.audio_codec,
        video_bitrate=request.video_bitrate,
        bitrate_quality_profile=request.bitrate_quality_profile,
        output_format=request.output_format,
        delete_input=request.delete_input_files,
        fallback_bitrate=request.fallback_bitrate,
        cap_dynamic_bitrate=request.cap_dynamic_bitrate,
        concurrent_conversions=request.concurrent_conversions,
        verbose_logging=request.verbose_logging,
    )

    return {
        "job_id": job.id,
        "status": "Conversion initiated.",
        "file_count": len(video_files),
        "files_to_process": [Path(f).name for f in video_files],
    }


@app.get("/status/{job_id}", response_model=schemas.Job, tags=["Conversion"])
def get_job_status(
    job_id: uuid.UUID,
    db: sqlite3.Connection = Depends(get_db)
):
    """Retrieves the status and details of a specific conversion job."""
    log.info("Fetching status for job", job_id=str(job_id))
    job = database.get_job(db, job_id)
    if job is None:
        log.warning("Job not found", job_id=str(job_id))
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/health", tags=["Health"])
def health_check():
    """Performs a health check and returns FFmpeg version."""
    try:
        # Execute ffmpeg -version command
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW # Prevent opening a window on Windows
        )
        # The version info is typically in the first line of stdout
        ffmpeg_version = result.stdout.splitlines()[0]
        log.info("Health check successful", ffmpeg_version=ffmpeg_version)
        return {"status": "healthy", "ffmpeg_version": ffmpeg_version}
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        log.error("Health check failed: FFmpeg not found or failed to execute", error=str(e))
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": "FFmpeg not found or not executable. Please check the installation.",
            },
        )
