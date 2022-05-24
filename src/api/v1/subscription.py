from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db import models
from db import schemas
from db.config import get_session

router = APIRouter()


@router.get('',
            tags=['Subscriptions'],
            summary='Список всех подписок',
            description='Список всех подписох с их ценами',
            response_model=list[schemas.Subscription]
            )
async def subscriptions(db: AsyncSession = Depends(get_session)):
    subscriptions = await get_all(db)
    return subscriptions


async def get_all(data):
    queryset = await data.execute(select(models.SubscribeType))
    return queryset.scalars().all()