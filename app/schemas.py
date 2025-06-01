from pydantic import BaseModel

class ChatRequest(BaseModel):
    dialog_id: str
    user_message: str

class ChatResponse(BaseModel):
    dialog_id: str
    assistant_message: str

class MessageCreate(BaseModel):
    dialog_id: str
    role: str
    content: str