Бот для Telegram с интеграцией LLM (OpenAI), сохраняющий историю диалогов.

## 📌 Особенности
- Диалог с поддержкой контекста (история сообщений)
- Интеграция с OpenAI API
- Хранение истории в SQLite
- FastAPI backend
- Поддержка асинхронных запросов

## 🚀 Установка

### Требования
- Python 3.11+
- Telegram Bot Token
- OpenAI API Key

### 1. Клонирование репозитория
```bash
git clone https://github.com/nastyona1998/LLM-bot.git
cd LLM-bot
```

### 2. Настройка окружения
Создайте файл .env в корне проекта:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
OPENAI_API_KEY=your_openai_key
DATABASE_URL=sqlite:///./sql_app.db
```

3. Установка зависимостей
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

4. Запуск
```bash
# Запуск FastAPI сервера
uvicorn app.main:app --reload

# В другом терминале запустите бота
python app/bot.py
```

## Пример запроса

```json
{
  "dialog_id": "test123",
  "user_message": "Привет"
}
```

## 🛠️ Структура проекта

```
.
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI приложение
│   ├── bot.py           # Telegram бот
│   ├── models.py        # Модели данных
│   ├── database.py      # Работа с БД
│   ├── llm_service.py   # Сервис работы с LLM
│   ├── config.py        # Конфигурация
│   └── schemas.py       # Pydantic схемы
└── tests/               # Тесты (опционально)
```