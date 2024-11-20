from project.db.config import POSTGRES_DB ,POSTGRES_HOST, POSTGRES_USER ,POSTGRES_PASSWORD, POSTGRES_PORT
import asyncio 
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


username = POSTGRES_USER
password = POSTGRES_PASSWORD
host = POSTGRES_HOST
port = POSTGRES_PORT
database = POSTGRES_DB

# Создаем строку подключения
connection_string = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"

engine = create_async_engine(connection_string, echo=True, pool_size=20, max_overflow=-1)

# Создаем фабрику сессий
set_session = sessionmaker(
    engine, 
    expire_on_commit=False, 
    class_=AsyncSession
)

async def get_session() -> AsyncSession:
    async with set_session() as session:
        return session