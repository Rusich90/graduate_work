import uuid
from abc import ABC
from abc import abstractmethod
from functools import lru_cache

import httpx
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.settings import BillingSettings
from db.config import get_session
from db.models import SubscribeType

config = BillingSettings()

class AbstractBilling(ABC):

    @abstractmethod
    async def payment(self, body):
        pass


class YookassaBilling(AbstractBilling):
    account_id = config.id
    secret_key = config.token.get_secret_value()
    url = config.url
    redirect_url = config.redirect_url

    def __init__(self, session):
        self.session = session

    async def payment(self, body):
        payment_info = await self._get_payment_info(body)
        headers = {'Idempotence-Key': await self._get_idempotence_key()}
        async with httpx.AsyncClient(auth=(str(self.account_id), self.secret_key)) as client:
            response = await client.post(self.url, headers=headers, json=payment_info)
        return response

    async def _get_payment_info(self, body):
        subscribe_type = await self.session.get(SubscribeType, body.subscribe_type_id)
        payment_info = {
            "amount": {
                "value": float(subscribe_type.price),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": self.redirect_url
            },
            "capture": True,
            "description": f"Оплата подписки {subscribe_type.name} на месяц",
            "save_payment_method": True
        }
        return payment_info

    async def _get_idempotence_key(self):
        return str(uuid.uuid4())


@lru_cache()
def get_billing_service(session: AsyncSession = Depends(get_session)) -> YookassaBilling:
    return YookassaBilling(session)
