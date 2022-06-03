from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from core.settings import DatabaseSettings

engine = create_async_engine(DatabaseSettings().db_url(), future=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


async def get_session():
    async with async_session() as session:
        async with session.begin():
            yield session
