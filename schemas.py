from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from datetime import datetime
import uuid

class JobStatus(str, Enum):
    """Enum for job statuses."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class JobBase(BaseModel):
    """Base model for a job."""
    pass

class JobCreate(JobBase):
    """Model for creating a new job."""
    pass

class Job(JobBase):
    """Model representing a job in the database."""
    id: uuid.UUID
    correlation_id: str | None = None
    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0
    logs: list[str] = []
    result: list[str] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ConversionRequest(BaseModel):
    """Model for the /convert endpoint request body."""
    input_directory: str
    output_directory: str
    video_codec: str = "hevc_nvenc"
    audio_codec: str = "aac"
    output_format: str = "mp4"
    video_bitrate: str = "optimized"
    bitrate_quality_profile: str = "Balanced Quality"
    delete_input_files: bool = False
    fallback_bitrate: str = "6M"
    cap_dynamic_bitrate: bool = True
    concurrent_conversions: int = 2
    verbose_logging: bool = False
