from pydantic import BaseModel
from typing import List, Dict, Optional

class ChatRequest(BaseModel):
    dialog_id: str
    user_message: str

class ChatResponse(BaseModel):
    dialog_id: str
    assistant_message: str
    history: Optional[List[Dict[str, str]]] = None

class MessageCreate(BaseModel):
    dialog_id: str
    role: str
    content: str