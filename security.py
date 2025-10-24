from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def api_key_auth(api_key: str = Security(api_key_header)):
    """Dependency to verify the API key if it is configured."""
    # If no API_KEY is configured in settings, authentication is disabled.
    if not settings.API_KEY:
        return

    # If an API_KEY is configured, but none is provided in the header.
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key required."
        )

    # If the provided API key does not match the configured one.
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key."
        )
