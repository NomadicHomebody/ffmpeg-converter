from fastapi import FastAPI, HTTPException
from asgi_correlation_id import CorrelationIdMiddleware
import structlog
import subprocess

from logging_config import configure_logging

# Configure logging before initializing the app
configure_logging()

app = FastAPI(
    title="FFMPEG Bulk Converter API",
    description="An API for bulk video conversion using FFMPEG.",
    version="1.0.0",
)

app.add_middleware(CorrelationIdMiddleware)

log = structlog.get_logger()


@app.get("/")
def read_root():
    """A welcome message for the API root."""
    log.info("Root endpoint was hit")
    return {"message": "Welcome to the FFMPEG Bulk Converter API"}


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
