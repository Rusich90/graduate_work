from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.responses import RedirectResponse
from sqlalchemy.future import select

from core.authentication import User
from core.authentication import get_user
from db import models
from db.config import AsyncSession
from db.config import get_session
from db.models import SubscribeType
from db.schemas import OkBody
from db.schemas import Transaction
from db.schemas import TransactionCreate
from services.billing import AbstractBilling
from services.billing import get_billing_service
from services.database import AbstractDatabase
from services.database import get_db

router = APIRouter()


@router.get('', response_model=list[Transaction])
async def user_transactions(db: AsyncSession = Depends(get_session),
                            current_user: User = Depends(get_user)):
    queryset = await db.execute(select(models.Transaction).where(models.Transaction.user_id == current_user.id))
    transactions = queryset.scalars().all()
    return transactions


@router.post('', status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def payment(body: TransactionCreate,
                  billing: AbstractBilling = Depends(get_billing_service),
                  db: AsyncSession = Depends(get_session),
                  current_user: User = Depends(get_user)):
    subscribe_type = await db.get(SubscribeType, body.subscribe_type_id)
    if not subscribe_type:
        msg = "Not correct id"
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
    payment_url = await billing.get_payment_url(subscribe_type, current_user)
    return RedirectResponse(payment_url)


@router.get('/redirect', status_code=status.HTTP_200_OK, response_model=OkBody)
async def redirect_url():
    return OkBody(detail='ok')


@router.post('/callback', status_code=status.HTTP_200_OK, response_model=OkBody )
async def payment_callback(request: Request, db: AbstractDatabase = Depends(get_db)):
    payment = await request.json()
    print(payment['object'])
    transaction = await db.update_transaction_status(payment)
    if transaction.status == 'succeeded':
        await db.create_subscribe(transaction)
    return OkBody(detail='ok')
