from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from core.authentication import User
from core.authentication import get_user
from db.schemas import SubscriptionBaseSchema
from db.schemas import SubscriptionSchema
from db.schemas import SubscriptionTypeSchema
from db.schemas import SubscriptionUpdateSchema
from services.database import AbstractDatabase
from services.database import get_db

router = APIRouter()


@router.get('',
            tags=['Subscriptions'],
            summary='Список текущих подписок юзера',
            response_model=list[SubscriptionSchema])
async def user_subscriptions(db: AbstractDatabase = Depends(get_db),
                             current_user: User = Depends(get_user)):
    subscriptions = await db.get_all_user_subscriptions(current_user.id)
    return subscriptions


@router.patch('/{subscription_id}',
              tags=['Subscriptions'],
              summary='Отмена автоподписки',
              response_model=SubscriptionBaseSchema)
async def update_renewal(body: SubscriptionUpdateSchema,
                         subscription_id: UUID,
                         db: AbstractDatabase = Depends(get_db),
                         current_user: User = Depends(get_user)):
    subscribe = await db.get_subscribe(subscription_id)

    if not subscribe:
        msg = "Not correct id"
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
    if subscribe.user_id != current_user.id:
        msg = "You don't have enough permission"
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=msg)

    updated_subscribe = await db.update_renewal(subscribe, body.auto_renewal)
    return updated_subscribe


@router.get('/types',
            tags=['Subscriptions'],
            summary='Список типов подписок',
            description='Список всех подписох с их ценами',
            response_model=list[SubscriptionTypeSchema]
            )
async def subscription_types(db: AbstractDatabase = Depends(get_db)):
    subscriptions_types = await db.get_all_subscription_types()
    return subscriptions_types
