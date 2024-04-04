from typing import AsyncGenerator
from core.config import app_settings
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine(str(app_settings.database_dsn), future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        return session


# При использовании конструкции из лекции:  


# async def get_session() -> AsyncSession:
#     async with async_session() as session:
#         yield session 

    
# Ошибка TypeError: object async_generator can't be used in 'await' expression
