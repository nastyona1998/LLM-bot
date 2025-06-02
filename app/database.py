from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine
from app.config import settings
from app.models import Base

# Создаём асинхронный движок для работы с базой данных
engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, echo=True)
# Создаём фабрику асинхронных сессий
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Асинхронная функция инициализации базы данных (создаёт таблицы, если их нет)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Асинхронный генератор для получения сессии работы с базой данных
async def get_db() -> AsyncSession:
    try:
        async with AsyncSessionLocal() as db:
            yield db
    except Exception as e:
        print(f"Ошибка сессии базы данных: {e}")
        raise