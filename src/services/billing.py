import logging
from abc import ABC
from abc import abstractmethod
from functools import lru_cache

import httpx
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from core.settings import BillingSettings
from db.cache import AbstractCache
from db.cache import get_cache
from services.database import AbstractDatabase
from services.database import get_db

logger = logging.getLogger(__name__)

config = BillingSettings()


class AbstractBilling(ABC):

    @abstractmethod
    async def get_payment_url(self, subscribe_type, current_user):
        pass


class YookassaBilling(AbstractBilling):
    account_id = config.id
    secret_key = config.token.get_secret_value()
    url = config.url
    redirect_url = config.redirect_url

    def __init__(self, db: AbstractDatabase, cache: AbstractCache):
        self.db = db
        self.cache = cache
        self.idempotence_key = None

    async def _payment_request(self, subscribe_type):
        payment_info = await self._get_payment_info(subscribe_type)
        headers = {'Idempotence-Key': self.idempotence_key }
        async with httpx.AsyncClient(auth=(str(self.account_id), self.secret_key)) as client:
            response = await client.post(self.url, headers=headers, json=payment_info)
        return response

    async def _get_payment_info(self, subscribe_type):
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

    @staticmethod
    async def _get_idempotence_key( user_id: str, subscribe_id: int):
        return str(f'{user_id}_{subscribe_id}')

    async def get_payment_url(self, subscribe_type, current_user):
        self.idempotence_key = await self._get_idempotence_key(current_user.id, subscribe_type.id)
        payment_url = await self.cache.get(self.idempotence_key)
        if not payment_url:
            logger.debug('Url not in cache')
            response = await self._payment_request(subscribe_type)
            if response.status_code != status.HTTP_200_OK:
                logger.error(response.json())
                msg = 'Something goes wrong'
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=msg)
            payment = response.json()
            logger.debug(payment)
            payment_url = await self.db.create_transaction(payment, subscribe_type, current_user)
            await self.cache.set(self.idempotence_key, payment_url)
            logger.debug('Url added in cache')
        logger.info(payment_url)
        return payment_url


@lru_cache()
def get_billing_service(db: AbstractDatabase = Depends(get_db),
                        cache: AbstractCache = Depends(get_cache)) -> YookassaBilling:
    return YookassaBilling(db, cache)
