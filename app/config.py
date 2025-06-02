from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    TELEGRAM_BOT_TOKEN: str
    DATABASE_URL: str = "sqlite+aiosqlite:///./sql_app.db"

    class Config:
        env_file = ".env"


settings = Settings()