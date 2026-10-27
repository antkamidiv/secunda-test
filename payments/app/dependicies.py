from uuid import UUID

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.settings import settings

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)


async def check_api_key_header(api_key: str = Security(api_key_header)):
    if api_key is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing api key")

    try:
        if UUID(api_key) != settings.api_key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid api key")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid api key format")
