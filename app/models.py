from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

# Базовый класс для всех моделей SQLAlchemy
Base = declarative_base()

# Модель сообщения для хранения в базе данных
class Message(Base):
    __tablename__ = "messages"  # Имя таблицы в базе данных

    id = Column(Integer, primary_key=True, index=True)  # Уникальный идентификатор сообщения
    dialog_id = Column(String, index=True)  # Идентификатор диалога
    role = Column(String)  # Роль: 'user' или 'assistant'
    content = Column(Text)  # Текст сообщения
    created_at = Column(DateTime, default=func.now())  # Время создания сообщения