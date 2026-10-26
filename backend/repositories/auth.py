import uuid
from typing import Any

from httpxC.http_client import http_client
from schemas.user import UserToken, AuthorizedUser
from core.config import settings
from core.retry import build_http_retry


@build_http_retry(attempts=2)
async def login_user(username: str, password: str) -> str:
    auth_endpoint: str = f"{settings.auth_api_url}/api/v1/auth/login"
    response = await http_client.post(
        auth_endpoint,
        json={
            "email": username,
            "password": password,
            "internal": True
        },
    )
    response.raise_for_status()
    data: dict[str, Any] = response.json()
    token: str = data.get("token", "")

    if token == "":
        raise ValueError("Token not found in response data")

    return token


@build_http_retry(attempts=2)
async def get_user_from_token(token: str) -> AuthorizedUser | None:
    auth_endpoint = f"{settings.auth_api_url}/api/v1/auth/me"
    headers = {"token": token}
    response = await http_client.post(auth_endpoint, headers=headers)
    response.raise_for_status()
    data = response.json()

    if not data or "id" not in data or "username" not in data:
        return None
    return AuthorizedUser(
        id=uuid.UUID(data.get("id", "")),
        username=data.get("username", ""),
        is_admin=data.get("is_admin", False),
    )


async def blacklist_token(token: str) -> bool:
    auth_endpoint: str = f"{settings.auth_api_url}/api/v1/auth/logout"
    response = await http_client.post(
        auth_endpoint,
        headers={"Authorization": f"Bearer {token}"},
    )
    if response.status_code == 200:
        return True
    return False


async def register_user(email: str, password: str) -> dict[str, Any]:
    auth_endpoint: str = f"{settings.auth_api_url}/api/v1/users/create"
    response = await http_client.post(
        auth_endpoint,
        json={"email": email, "password": password},
    )
    data = response.json()
    if data.get("message") == "User with this email already exists":
        return {"ok": False, "error": data.get("message")}

    if data.get("ok") == True:
        return {"ok": True, "user_id": data.get("user_id", -1)}

    return {"ok": False, "error": "User creation failed"}


@build_http_retry(attempts=2)
async def internal_api_login() -> bool:
    user_token: UserToken | bool = await login_user(
        settings.internal_api_username,
        settings.internal_api_password,
    )
    if type(user_token) is bool:
        return user_token

    settings.internal_cookie = user_token.token
    return True
