from fastapi import FastAPI
from asgi_correlation_id import CorrelationIdMiddleware
import structlog

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
