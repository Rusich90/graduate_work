import datetime
import logging
from abc import ABC
from abc import abstractmethod

import sqlalchemy.exc
from dateutil.relativedelta import relativedelta
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.authentication import User
from db.config import get_session
from db.models import Subscribe
from db.models import SubscribeType
from db.models import Transaction

logger = logging.getLogger(__name__)


class AbstractDatabase(ABC):

    @abstractmethod
    async def create_transaction(self, subscribe_type: Subscribe, current_user: User):
        pass

    @abstractmethod
    async def create_subscribe(self, transaction: Transaction):
        pass

    @abstractmethod
    async def update_transaction(self, payment: dict):
        pass


class AlchemyDatabase(AbstractDatabase):

    def __init__(self, session):
        self.session = session

    async def create_transaction(self, subscribe_type: SubscribeType, current_user: User) -> Transaction:
        transaction = Transaction(
            user_id=current_user.id,
            subscribe_type_id=subscribe_type.id,
            amount=float(subscribe_type.price),
            description=f"Оплата подписки {subscribe_type.name} на месяц",
            status="pending",
        )
        self.session.add(transaction)
        await self.session.flush()
        return transaction

    async def create_subscribe(self, transaction: Transaction) -> None:
        today = datetime.date.today()
        print(transaction)
        subscribe = Subscribe(
            user_id=transaction.user_id,
            transaction_id=transaction.id,
            subscribe_type_id=transaction.subscribe_type_id,
            start_date=today,
            end_date=today + relativedelta(months=+1),
        )
        try:
            self.session.add(subscribe)
            await self.session.flush()
        except sqlalchemy.exc.IntegrityError:
            logger.error('Duplicate transaction_id')
        # TODO: Add kafka producer to AUTH

    async def update_transaction(self, payment: dict) -> Transaction:
        query = await self.session.execute(select(Transaction).where(
            Transaction.aggregator_id == payment['object']['id']
        ))
        transaction = query.scalar()
        transaction.status = payment['object']['status']
        if transaction.status == 'canceled':
            transaction.failed_reason = payment['object']['cancellation_details']['reason']
        transaction.card_4_numbers = int(payment['object']['payment_method']['card']['last4'])
        return transaction


async def get_db(session: AsyncSession = Depends(get_session)) -> AlchemyDatabase:
    return AlchemyDatabase(session)
