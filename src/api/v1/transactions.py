import logging

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.responses import RedirectResponse
from sqlalchemy.future import select

from core.authentication import User
from core.authentication import get_user
from db.config import AsyncSession
from db.config import get_session
from db.models import SubscribeType
from db.models import Transaction
from db.schemas import OkBody
from db.schemas import TransactionDetail
from db.schemas import TransactionCreate, TransactionRefund
from services.billing import AbstractBilling
from services.billing import get_billing_service
from services.database import AbstractDatabase
from services.database import get_db

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get('',
            tags=['Transactions'],
            summary='Список всех транзакций юзера',
            response_model=list[TransactionDetail])
async def user_transactions(db: AsyncSession = Depends(get_session),
                            current_user: User = Depends(get_user)):
    queryset = await db.execute(select(Transaction).where(Transaction.user_id == current_user.id))
    transactions = queryset.scalars().all()
    return transactions


@router.post('',
             tags=['Transactions'],
             summary='Создание новой транзакции',
             status_code=status.HTTP_302_FOUND)
async def payment(body: TransactionCreate,
                  billing: AbstractBilling = Depends(get_billing_service),
                  db: AsyncSession = Depends(get_session),
                  current_user: User = Depends(get_user)):
    subscribe_type = await db.get(SubscribeType, body.subscribe_type_id)
    if not subscribe_type:
        msg = "Not correct id"
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
    payment_url = await billing.get_payment_url(subscribe_type, current_user)
    return RedirectResponse(payment_url, status_code=status.HTTP_302_FOUND)


@router.get('/redirect',
            tags=['Transactions'],
            summary='Эндпоинты для редиректа после аггрегатора',
            status_code=status.HTTP_200_OK,
            response_model=OkBody)
async def redirect_url():
    return OkBody(detail='ok')


@router.post('/callback',
             tags=['Transactions'],
             summary='Эндпоинты для коллбэка от аггрегатора',
             status_code=status.HTTP_200_OK,
             response_model=OkBody)
async def payment_callback(request: Request, db: AbstractDatabase = Depends(get_db),
                           billing: AbstractBilling = Depends(get_billing_service)):
    logger.info(await request.json())
    payment = await billing.get_payment_object(await request.json(), card=True)
    transaction = await db.update_transaction(payment)
    if transaction.status == 'succeeded':
        await db.create_subscribe(transaction)
    return OkBody(detail='ok')


@router.post('/refund',
             tags=['Transactions'],
             summary='Возврат средств'
             )
async def payment(body: TransactionRefund,
                  billing: AbstractBilling = Depends(get_billing_service),
                  db: AsyncSession = Depends(get_session),
                  current_user: User = Depends(get_user)):
    transaction = await db.get(Transaction, body.transaction_id)
    if not transaction or transaction.user_id != current_user.id:
        msg = "Not correct id"
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
    await billing.refund_payment(transaction)
    return OkBody(detail='ok')
