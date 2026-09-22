import os

from fastapi import Header, HTTPException, Depends

# Read the expected API key from an environment variable.
# Falls back to a dev key so the app works out of the box.
API_KEY = os.getenv("API_KEY", "dev-api-key-change-me")


async def verify_api_key(x_api_key: str = Header(default=None)):
    """
    FastAPI dependency that checks the X-API-Key header.
    Pass `x_api_key=None` to skip auth (header omitted) — we treat that as
    unauthenticated but still allowed in dev mode for convenience.
    In production you'd make this mandatory.
    """
    if x_api_key is not None and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key
