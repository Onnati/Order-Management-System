from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    database_url: str = "postgresql://orderapp:orderapp_secret@localhost:5432/order_management"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True


settings = Settings()
