from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    cookie_key: str
    auth_api_url: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
