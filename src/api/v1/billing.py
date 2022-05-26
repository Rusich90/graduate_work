from fastapi import APIRouter
from fastapi import Depends
from fastapi import status, HTTPException
from fastapi import Request
from fastapi.responses import RedirectResponse

from core.authentication import get_user, User
from db.schemas import TransactionCreate
from services.billing import AbstractBilling
from services.billing import get_billing_service
from services.database import AbstractDatabase
from services.database import get_db
from db.config import get_session, AsyncSession
from db.models import SubscribeType
from db.schemas import OkBody

router = APIRouter()


@router.post('', status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def billing(body: TransactionCreate,
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
async def billing():
    return OkBody(detail='ok')


@router.post('/callback', status_code=status.HTTP_200_OK, response_model=OkBody )
async def billing(request: Request, db: AbstractDatabase = Depends(get_db)):
    payment = await request.json()
    print(payment['object'])
    transaction = await db.update_transaction_status(payment)
    if transaction.status == 'succeeded':
        await db.create_subscribe(transaction)
    return OkBody(detail='ok')
