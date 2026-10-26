from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    cookie_key: str
    auth_api_url: str
    cookie_secure: bool = False
    frontend_url: str | None = None
    scrappys_api_key: str | None = None
    internal_api_username: str | None = None
    internal_api_password: str | None = None
    internal_cookie: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
