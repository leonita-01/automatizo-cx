from hmac import compare_digest

from fastapi import Header, HTTPException, status

from ..config import settings


def require_admin_key(x_admin_key: str | None = Header(default=None)) -> None:
    if not x_admin_key or not compare_digest(x_admin_key, settings.admin_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid X-Admin-Key header is required",
        )
