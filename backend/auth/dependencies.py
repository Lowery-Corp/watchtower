from fastapi import Cookie, HTTPException, status, Request

from core.config import settings
from repositories.auth import get_user_from_token
from schemas.user import AuthorizedUser

def require_admin_user(request: Request) -> None:
    request_auth_key = request.headers.get("api-key")
    if request_auth_key != settings.scrappys_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

async def get_current_user(
    access_token: str | None = Cookie(default=None, alias=settings.cookie_key)
) -> AuthorizedUser:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    authorized_user = await get_user_from_token(token=access_token)

    if not authorized_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return authorized_user