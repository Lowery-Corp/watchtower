import uuid
from pydantic import BaseModel, EmailStr, field_validator

class UserCreate(BaseModel):
    username: EmailStr
    password: str

    @field_validator("username", mode="before")
    def normalize_email(cls, username: EmailStr) -> str:
        return username.strip().lower()

    @field_validator("password", mode="before")
    def validate_password(cls, password: str) -> str:
        password = password.strip()
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isalpha() for char in password):
            raise ValueError("Password must contain at least one letter")
        if not any(char in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for char in password):
            raise ValueError("Password must contain at least one special character")
        return password

class UserLogin(BaseModel):
    username: EmailStr
    password: str

    @field_validator("username", mode="before")
    def normalize_email(cls, username: EmailStr) -> str:
        return username.strip().lower()

class DeleteUser(BaseModel):
    email: EmailStr

    @field_validator("email", mode="before")
    def normalize_email(cls, email: EmailStr) -> str:
        return email.strip().lower()

class UserToken(BaseModel):
    token: str

class LoginResponse(BaseModel):
    username: EmailStr

class AuthorizedUser(BaseModel):
    id: uuid.UUID
    username: str
    is_admin: bool = False
