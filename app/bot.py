import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
import httpx

from app.config import settings
from app.schemas import ChatRequest
from app.llm_service import LLMService

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

API_URL = "http://127.0.0.1:8000/api/chat"

llm = LLMService()
system_prompt_text = llm.SYSTEM_PROMPT


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
            history = data.get("history")
            if history is None:
                await message.reply("Ошибка: сервер не вернул историю диалога.")
                return
            # Найдём system prompt (обычно это первый элемент в history)
            system_prompt = ""
            if history and history[0]["role"] == "system":
                system_prompt = f"*SYSTEM*: {system_prompt_text}\n"
                history = history[1:]  # убираем system prompt из дальнейшей истории

            history_text = "\n".join(
                f"*{msg['role']}*: {msg['content']}" for msg in history
            )
            await message.reply(system_prompt + history_text, parse_mode="Markdown")
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