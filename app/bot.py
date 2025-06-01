import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
import httpx

from app.config import settings
from app.schemas import ChatRequest

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

API_URL = "http://localhost:8000/api/chat"


class LoggingMiddleware:
    async def __call__(self, handler, event, data):
        logger.info(f"Processing update: {event}")
        return await handler(event, data)


async def process_message(message: types.Message):
    dialog_id = str(message.from_user.id)  # Используем ID пользователя как dialog_id

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                API_URL,
                json={
                    "dialog_id": dialog_id,
                    "user_message": message.text
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            await message.reply(data["assistant_message"])
        except httpx.HTTPError as e:
            logger.error(f"API request failed: {e}")
            await message.reply("Sorry, I'm having trouble connecting to the server. Please try again later.")


@dp.message(F.text)
async def handle_message(message: types.Message):
    await process_message(message)


async def on_startup():
    logger.info("Bot started")
    # Здесь можно добавить код инициализации
    dp.update.middleware.register(LoggingMiddleware())


async def main():
    await on_startup()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())