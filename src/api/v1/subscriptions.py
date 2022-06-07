from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from core.authentication import User
from core.authentication import get_user
from db.config import get_session
from db.models import Subscribe
from db.models import SubscribeType
from db.schemas import SubscriptionBaseSchema
from db.schemas import SubscriptionSchema
from db.schemas import SubscriptionTypeSchema
from db.schemas import SubscriptionUpdateSchema

router = APIRouter()


@router.get('',
            tags=['Subscriptions'],
            summary='Список текущих подписок юзера',
            response_model=list[SubscriptionSchema])
async def user_subscriptions(db: AsyncSession = Depends(get_session),
                             current_user: User = Depends(get_user)):
    queryset = select(Subscribe).where(
        Subscribe.user_id == current_user.id
    ).options(selectinload(Subscribe.subscribe_type))
    queryset = await db.execute(queryset)
    transactions = queryset.scalars().all()
    return transactions


@router.patch('/{subscription_id}',
              tags=['Subscriptions'],
              summary='Отмена автоподписки',
              response_model=SubscriptionBaseSchema)
async def user_subscriptions(body: SubscriptionUpdateSchema,
                             subscription_id: UUID,
                             db: AsyncSession = Depends(get_session),
                             current_user: User = Depends(get_user)):
    subscribe = await db.get(Subscribe, subscription_id)
    if not subscribe:
        msg = "Not correct id"
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
    if subscribe.user_id != current_user.id:
        msg = "You don't have enough permission"
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=msg)
    subscribe.auto_renewal = body.auto_renewal
    return subscribe


@router.get('/types',
            tags=['Subscriptions'],
            summary='Список типов подписок',
            description='Список всех подписох с их ценами',
            response_model=list[SubscriptionTypeSchema]
            )
async def subscription_types(db: AsyncSession = Depends(get_session)):
    queryset = await db.execute(select(SubscribeType))
    subscriptions = queryset.scalars().all()
    return subscriptions
