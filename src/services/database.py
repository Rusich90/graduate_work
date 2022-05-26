import datetime
from abc import ABC
from abc import abstractmethod

from dateutil.relativedelta import relativedelta
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.config import get_session
from db.models import Subscribe
from db.models import Transaction


class AbstractDatabase(ABC):

    @abstractmethod
    async def create_transaction(self, payment, subscribe_type, current_user):
        pass

    @abstractmethod
    async def create_subscribe(self, transaction):
        pass

    @abstractmethod
    async def update_transaction_status(self, payment):
        pass


class AlchemyDatabase(AbstractDatabase):

    def __init__(self, session):
        self.session = session

    async def create_transaction(self, payment, subscribe_type, current_user):
        transaction = Transaction(
            id=payment['id'],
            user_id=current_user.id,
            subscribe_type_id=subscribe_type.id,
            amount=float(payment['amount']['value']),
            description=payment['description'],
            status=payment['status'],
        )
        self.session.add(transaction)
        await self.session.commit()
        return payment['confirmation']['confirmation_url']

    async def create_subscribe(self, transaction):
        today = datetime.date.today()
        subscribe = Subscribe(
            user_id=transaction.user_id,
            transaction_id=transaction.id,
            subscribe_type_id=transaction.subscribe_type_id,
            start_date=today,
            end_date=today + relativedelta(months=+1),
        )
        self.session.add(subscribe)
        # TODO: Add kafka producer to AUTH

    async def update_transaction_status(self, payment):
        transaction = await self.session.get(Transaction, payment['object']['id'])
        transaction.status = payment['object']['status']
        if transaction.status == 'canceled':
            transaction.failed_reason = payment['object']['cancellation_details']['reason']
        return transaction


async def get_db(session: AsyncSession = Depends(get_session)) -> AlchemyDatabase:
    return AlchemyDatabase(session)
