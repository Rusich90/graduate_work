from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import RedirectResponse

from core.authentication import get_user
from db.schemas import TransactionCreate
from services.billing import AbstractBilling
from services.billing import get_billing_service
from services.database import AbstractDatabase
from services.database import get_db

router = APIRouter()


@router.post('')
async def billing(body: TransactionCreate,
                  billing: AbstractBilling = Depends(get_billing_service),
                  db: AbstractDatabase = Depends(get_db),
                  current_user = Depends(get_user)):
    response = await billing.payment(body)
    if response.status_code == 200:
        payment = response.json()
        payment_url = await db.create_transaction(payment, body, current_user)

        return RedirectResponse(payment_url)
    return HTTPException(status_code=500)


@router.get('/redirect')
async def billing():

    return {"result": "ok"}


@router.post('/callback')
async def billing(request: Request, db: AbstractDatabase = Depends(get_db)):
    payment = await request.json()
    print(payment['object'])
    transaction = await db.update_transaction_status(payment)
    if transaction.status == 'succeeded':
        await db.create_subscribe(transaction)
    return {"result": "callback"}
