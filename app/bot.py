import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
import httpx

from app.config import settings
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

# Получаем системный промпт из сервиса LLM
system_prompt_text = LLMService.SYSTEM_PROMPT


class LoggingMiddleware:
    async def __call__(self, handler, event, data):
        logger.info(f"Обработка обновления: {event}")
        return await handler(event, data)


# Основная функция обработки входящих сообщений пользователя
async def process_message(message: types.Message):
    dialog_id = str(message.from_user.id)  # Используем ID пользователя как dialog_id

    async with httpx.AsyncClient() as client:
        try:
            # Отправляем POST-запрос к backend API с dialog_id и текстом пользователя
            response = await client.post(
                API_URL,
                json={
                    "dialog_id": dialog_id,
                    "user_message": message.text
                },
                timeout=30.0
            )
            response.raise_for_status()
            try:
                data = response.json()
            except Exception as e:
                logger.error(f"Ошибка парсинга JSON от API: {e}")
                await message.reply("Ошибка сервера: не удалось обработать ответ.")
                return

            # Проверяем, вернула ли модель ошибку
            if "error" in data:
                logger.error(f"Ошибка от модели: {data['error']}")
                await message.reply(f"Ошибка от модели: {data['error']}")
                return

            history = data.get("history")
            if history is None:
                await message.reply("Ошибка: сервер не вернул историю диалога.")
                return

            # Находим system prompt (обычно это первый элемент в истории)
            system_prompt = ""
            if history and history[0]["role"] == "system":
                system_prompt = f"*SYSTEM*: {system_prompt_text}\n"
                history = history[1:]  # Убираем system prompt из дальнейшей истории

            # Формируем текст истории (роль и сообщение)
            history_text = "\n".join(
                f"*{msg['role']}*: {msg['content']}" for msg in history
            )
            await message.reply(system_prompt + history_text, parse_mode="Markdown")

        except httpx.TimeoutException:
            logger.error("Таймаут при обращении к API")
            await message.reply("Сервер долго не отвечает. Попробуйте позже.")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP ошибка от API: {e.response.status_code} {e.response.text}")
            await message.reply(f"Ошибка сервера: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Сетевая ошибка при обращении к API: {e}")
            await message.reply("Ошибка соединения с сервером. Попробуйте позже.")
        except Exception as e:
            logger.error(f"Неизвестная ошибка: {e}")
            await message.reply("Произошла неизвестная ошибка. Попробуйте позже.")

# Обработчик всех текстовых сообщений пользователя
@dp.message(F.text)
async def handle_message(message: types.Message):
    await process_message(message)

# Функция, выполняющаяся при старте бота
async def on_startup():
    logger.info("Бот запущен")
    # Регистрируем middleware для логирования
    dp.update.middleware.register(LoggingMiddleware())

# Основная точка входа для запуска бота
async def main():
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())