from pydantic import BaseModel
from typing import List, Dict, Optional

# Схема запроса для чата (от пользователя к API)
class ChatRequest(BaseModel):
    dialog_id: str  # Идентификатор диалога
    user_message: str  # Сообщение пользователя

# Схема ответа для чата (от API к пользователю)
class ChatResponse(BaseModel):
    dialog_id: str  # Идентификатор диалога
    assistant_message: str  # Ответ ассистента
    history: Optional[List[Dict[str, str]]] = None  # Вся история диалога

# Схема для создания нового сообщения в базе данных
class MessageCreate(BaseModel):
    dialog_id: str  # Идентификатор диалога
    role: str  # Роль: 'user' или 'assistant'
    content: str  # Текст сообщения