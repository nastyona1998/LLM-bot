from typing import List, Dict
import openai
from app.config import settings
from app.models import Message
from app.schemas import MessageCreate

# Создаём асинхронного клиента OpenAI с использованием API-ключа
client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class LLMService:
    # Системный промпт для LLM
    SYSTEM_PROMPT = "Ты — мастер жутких историй. Я буду отправлять тебе предложения, а ты продолжи сюжет одним предложением в жанре хоррор. Добавляй мрачные детали, атмосферу тревоги и неожиданные повороты. Не объясняй свои действия — только продолжение."

    # Асинхронная функция для генерации ответа от LLM
    async def generate_response(self, messages: List[Dict]) -> str:
        try:
            response = await client.chat.completions.create(
                model="o4-mini",
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Ошибка генерации ответа: {e}")
            return "Извините, произошла ошибка. Пожалуйста, попробуйте позже."

    # Формирует список сообщений для LLM (системный промпт + история + новое сообщение)
    def prepare_messages(self, db_messages: List[Message], user_message: str) -> List[Dict]:
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        for msg in db_messages:
            messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": user_message})

        return messages