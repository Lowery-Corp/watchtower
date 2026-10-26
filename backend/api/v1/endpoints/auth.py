from fastapi import APIRouter, Response, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db.dependencies import get_session
from schemas.user import UserLogin, UserCreate, AuthorizedUser, LoginResponse
from repositories.auth import (
    blacklist_token,
    register_user
)
from repositories.user import login
from schemas.user import AuthorizedUser
from auth.dependencies import get_current_user

router = APIRouter(tags=["auth"])

@router.post("/login")
async def login_route(
    UserLogin: UserLogin,
    response: Response,
) -> LoginResponse | dict[str, str | bool]:
    try:
        login_data = await login(UserLogin)

        response.set_cookie(
            key=settings.cookie_key,
            value=str(login_data.get("token")),
            httponly=True,
            secure=True,      # True in production over HTTPS
            samesite="lax",    # often fine for same-site frontend/backend
            max_age=60 * 60,
            expires=60 * 60,
            path="/",
        )

        user_data = login_data.get("user")
        if not isinstance(user_data, LoginResponse):
            raise ValueError("Invalid user data type")
        user: LoginResponse = user_data

        return user
    except Exception as e:
        response.status_code = 401
        return {"ok": False, "message": "Invalid username or password"}


@router.get("/me")
async def read_me_route(
    current_user: AuthorizedUser = Depends(get_current_user),
) -> dict[str, str]:
    return {"username": current_user.username}


@router.post("/logout")
async def logout_route(response: Response, request: Request) -> dict[str, bool]:
    token = request.cookies.get("access_token")

    if token:
        # decode token, get jti, store in blacklist table/cache
        blacklist_status = await blacklist_token(token)
        print("Blacklist status:", blacklist_status)

        response.delete_cookie(
            key="access_token",
            path="/",
        )
        return {"ok": True}
    return {"ok": False}


@router.post("/register")
async def register_route(
    new_user: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> dict[str, bool | str]:
    user_created = await register_user(
        email=new_user.email,
        password=new_user.password,
    )

    if user_created.get("ok") is not True:
        return {"ok": False, "message": user_created.get("error", "User creation failed")}

    return {"ok": True, "message": "User created successfully"}

