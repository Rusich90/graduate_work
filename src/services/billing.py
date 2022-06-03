import logging
from abc import ABC
from abc import abstractmethod
from functools import lru_cache
from typing import Optional
from uuid import UUID

import httpx
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from core.authentication import User
from core.settings import BillingSettings
from db.cache import AbstractCache
from db.cache import get_cache
from db.models import Subscribe
from db.models import SubscribeType
from db.models import Transaction
from services.database import AbstractDatabase
from services.database import get_db

logger = logging.getLogger(__name__)

config = BillingSettings()


class AbstractBilling(ABC):

    @abstractmethod
    async def get_payment_url(self, subscribe_type: SubscribeType, current_user: User) -> str:
        pass

    @abstractmethod
    async def auto_payment(self, subscribe: Subscribe):
        pass


class YookassaBilling(AbstractBilling):
    account_id = config.id
    secret_key = config.token.get_secret_value()
    url = config.url
    redirect_url = config.redirect_url

    def __init__(self, db: AbstractDatabase, cache: Optional[AbstractCache] = None):
        self.db = db
        self.cache = cache
        self.idempotence_key = None

    async def _payment_request(self, subscribe_type: SubscribeType, transaction: Transaction, aggregator_id=None):
        payment_info = await self._get_payment_info(subscribe_type, transaction, aggregator_id)
        headers = {'Idempotence-Key': str(transaction.id)}
        async with httpx.AsyncClient(auth=(str(self.account_id), self.secret_key)) as client:
            response = await client.post(self.url, headers=headers, json=payment_info)
        return response

    async def _get_payment_info(self, subscribe_type: SubscribeType, transaction: Transaction, aggregator_id=None) -> dict:
        payment_info = {
            "amount": {
                "value": float(subscribe_type.price),
                "currency": "RUB"
            },
            "capture": True,
            "description": transaction.description,
        }
        if aggregator_id:
            payment_info['payment_method_id'] = str(aggregator_id)
        else:
            payment_info['save_payment_method'] = True
            payment_info['confirmation'] = {
                "type": "redirect",
                "return_url": self.redirect_url
            }
        return payment_info

    @staticmethod
    async def _get_idempotence_key(user_id: UUID, subscribe_id: int):
        return str(f'{user_id}_{subscribe_id}')

    async def get_payment_url(self, subscribe_type, current_user):
        self.idempotence_key = await self._get_idempotence_key(current_user.id, subscribe_type.id)
        payment_url = await self.cache.get(self.idempotence_key)
        if not payment_url:
            logger.debug('Url not in cache')
            transaction = await self.db.create_transaction(subscribe_type, current_user)
            response = await self._payment_request(subscribe_type, transaction)
            if response.status_code != status.HTTP_200_OK:
                logger.error(response.json())
                msg = 'Something goes wrong'
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=msg)
            payment = response.json()
            transaction.status = payment['status']
            transaction.aggregator_id = payment['id']
            logger.debug(payment)
            payment_url = payment['confirmation']['confirmation_url']
            await self.cache.set(self.idempotence_key, payment_url)
            logger.debug('Url added in cache')
        logger.info(payment_url)
        return payment_url

    async def auto_payment(self, subscribe: Subscribe):
        user = User(id=subscribe.user_id)
        aggregator_id = subscribe.transaction.aggregator_id
        transaction = await self.db.create_transaction(subscribe.subscribe_type, user)
        response = await self._payment_request(subscribe.subscribe_type, transaction, aggregator_id)
        if response.status_code != status.HTTP_200_OK:
            logger.error(response.json())
            msg = 'Something goes wrong'
            # TODO: Add some logic
        payment = response.json()
        logger.info(payment)
        transaction.status = payment['status']
        transaction.aggregator_id = payment['id']
        transaction.card_4_numbers = int(payment['payment_method']['card']['last4'])
        logger.debug(payment)
        await self.db.update_subscribe(subscribe)


@lru_cache()
def get_billing_service(db: AbstractDatabase = Depends(get_db),
                        cache: AbstractCache = Depends(get_cache)) -> YookassaBilling:
    return YookassaBilling(db, cache)
