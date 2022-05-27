from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from core.authentication import User
from core.authentication import get_user
from db.config import get_session
from db.models import Subscribe
from db.models import SubscribeType
from db.schemas import SubscriptionSchema
from db.schemas import SubscriptionTypeSchema

router = APIRouter()


@router.get('', response_model=list[SubscriptionSchema])
async def user_subscriptions(db: AsyncSession = Depends(get_session),
                             current_user: User = Depends(get_user)):
    queryset = select(Subscribe).where(Subscribe.user_id == current_user.id).options(selectinload(Subscribe.subscribe_type))
    queryset = await db.execute(queryset)
    transactions = queryset.scalars().all()
    return transactions


@router.get('/types',
            tags=['Subscriptions'],
            summary='Список всех подписок',
            description='Список всех подписох с их ценами',
            response_model=list[SubscriptionTypeSchema]
            )
async def subscription_types(db: AsyncSession = Depends(get_session)):
    queryset = await db.execute(select(SubscribeType))
    subscriptions = queryset.scalars().all()
    return subscriptions
