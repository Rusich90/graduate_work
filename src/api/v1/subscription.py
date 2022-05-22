from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db import models
from db import schemas
from db.config import async_session

router = APIRouter()


async def get_db():
    async with async_session() as session:
        async with session.begin():
            yield session

@router.get('',
            tags=['Subscriptions'],
            summary='Список всех подписок',
            description='Список всех подписох с их ценами',
            response_model=list[schemas.Subscription]
            )
async def subscriptions(db: AsyncSession = Depends(get_db)):
    subscriptions = await get_all(db)
    return subscriptions


async def get_all(data):
    queryset = await data.execute(select(models.Subscription))
    return queryset.scalars().all()