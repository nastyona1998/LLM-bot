from pydantic_settings import BaseSettings

# Класс настроек приложения, использует pydantic для валидации и загрузки переменных окружения
class Settings(BaseSettings):
    OPENAI_API_KEY: str  # Ключ API для доступа к OpenAI
    TELEGRAM_BOT_TOKEN: str  # Токен Telegram-бота
    DATABASE_URL: str = "sqlite+aiosqlite:///./sql_app.db"  # URL для подключения к базе данных

    class Config:
        env_file = ".env"  # Имя файла с переменными окружения

# Создаём экземпляр настроек, который будет использоваться во всём приложении
settings = Settings()