from fastapi import APIRouter, Depends, HTTPException, Request
from services.billing import AbstractBilling, get_billing_service
from fastapi.responses import RedirectResponse

router = APIRouter()

@router.get('',
            tags=['Billing'],
            summary='Список всех жанров',
            description='Список всех жанров. Можно изменить size запроса и сделать поиск по названию жанра',
            )
async def billing(billing: AbstractBilling = Depends(get_billing_service)):
    payment = billing.payment()
    print(payment['confirmation']['confirmation_url'])
    print(payment)
    return RedirectResponse(payment['confirmation']['confirmation_url'])

@router.get('/redirect',
            tags=['Billing'],
            summary='Список всех жанров',
            description='Список всех жанров. Можно изменить size запроса и сделать поиск по названию жанра',
            )
async def billing():

    return {"result": "ok"}


@router.post('/callback')
async def billing(request: Request):
    print(await request.json())
    return {"result": "callback"}
