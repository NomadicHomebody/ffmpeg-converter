from fastapi import FastAPI

app = FastAPI(
    title="FFMPEG Bulk Converter API",
    description="An API for bulk video conversion using FFMPEG.",
    version="1.0.0",
)

@app.get("/")
def read_root():
    """A welcome message for the API root."""
    return {"message": "Welcome to the FFMPEG Bulk Converter API"}
