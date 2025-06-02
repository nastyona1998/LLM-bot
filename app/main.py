from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas, models, database, llm_service
from app.database import get_db, init_db

# Создаём экземпляр FastAPI-приложения
app = FastAPI()

# При запуске приложения инициализируем базу данных (создаём таблицы, если их нет)
@app.on_event("startup")
async def on_startup():
    await init_db()

# Настройка CORS для разрешения запросов с любых источников (для разработки)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация сервиса работы с LLM
llm = llm_service.LLMService()

# Основной эндпоинт для общения с LLM через POST-запрос
@app.post("/api/chat", response_model=schemas.ChatResponse)
async def chat(
        request: schemas.ChatRequest,
        db: AsyncSession = Depends(get_db)
):
    # Получаем всю историю сообщений по dialog_id, отсортированную по времени
    result = await db.execute(
        select(models.Message)
        .where(models.Message.dialog_id == request.dialog_id)
        .order_by(models.Message.created_at)
    )
    db_messages = result.scalars().all()

    # Формируем payload для LLM (системный промпт + история + новое сообщение)
    messages = llm.prepare_messages(db_messages, request.user_message)

    # Получаем ответ от LLM
    assistant_message = await llm.generate_response(messages)

    # Сохраняем сообщение пользователя в базу данных
    user_msg = models.Message(
        dialog_id=request.dialog_id,
        role="user",
        content=request.user_message
    )
    db.add(user_msg)

    # Сохраняем ответ ассистента в базу данных
    assistant_msg = models.Message(
        dialog_id=request.dialog_id,
        role="assistant",
        content=assistant_message
    )
    db.add(assistant_msg)

    # Фиксируем изменения в базе данных
    await db.commit()

    # Возвращаем ответ с историей диалога
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