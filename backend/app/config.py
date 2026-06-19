from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    database_url: str = "postgresql://orderapp:orderapp_secret@localhost:5432/order_management"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True

    @field_validator("database_url", mode="before")
    @classmethod
    def fix_postgres_scheme(cls, value: str) -> str:
        if isinstance(value, str) and value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql://", 1)
        return value


settings = Settings()
