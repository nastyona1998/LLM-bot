from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas, models, database, llm_service
from app.database import get_db, init_db

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await init_db()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = llm_service.LLMService()


@app.post("/api/chat", response_model=schemas.ChatResponse)
async def chat(
        request: schemas.ChatRequest,
        db: AsyncSession = Depends(get_db)
):
    # Получаем историю диалога
    result = await db.execute(
        select(models.Message)
        .where(models.Message.dialog_id == request.dialog_id)
        .order_by(models.Message.created_at)
    )
    db_messages = result.scalars().all()

    # Подготавливаем сообщения для LLM
    messages = llm.prepare_messages(db_messages, request.user_message)

    # Получаем ответ от LLM
    assistant_message = await llm.generate_response(messages)

    # Сохраняем сообщение пользователя
    user_msg = models.Message(
        dialog_id=request.dialog_id,
        role="user",
        content=request.user_message
    )
    db.add(user_msg)

    # Сохраняем ответ ассистента
    assistant_msg = models.Message(
        dialog_id=request.dialog_id,
        role="assistant",
        content=assistant_message
    )
    db.add(assistant_msg)

    await db.commit()

    return {
        "dialog_id": request.dialog_id,
        "assistant_message": assistant_message,
        "history": (
            [{"role": "system", "content": llm.SYSTEM_PROMPT}]
            + [{"role": msg.role, "content": msg.content} for msg in db_messages]
            + [{"role": "user", "content": request.user_message},
               {"role": "assistant", "content": assistant_message}]
        )
    }