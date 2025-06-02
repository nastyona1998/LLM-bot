from typing import List, Dict
import openai
from app.config import settings
from app.models import Message
from app.schemas import MessageCreate

# Создаём асинхронного клиента OpenAI
client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class LLMService:
    SYSTEM_PROMPT = "You are a helpful assistant. Answer concisely and clearly."

    async def generate_response(self, messages: List[Dict]) -> str:
        try:
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Sorry, I encountered an error. Please try again later."

    def prepare_messages(self, db_messages: List[Message], user_message: str) -> List[Dict]:
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        for msg in db_messages:
            messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": user_message})

        return messages