import datetime
import logging
from abc import ABC
from abc import abstractmethod
from datetime import date

import sqlalchemy.exc
from dateutil.relativedelta import relativedelta
from fastapi import Depends
from sqlalchemy import Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from core.authentication import User
from db.config import get_session
from db.models import Subscribe
from db.models import SubscribeType
from db.models import Transaction
from db.models import Refund
from db.schemas import Payment

logger = logging.getLogger(__name__)


class AbstractDatabase(ABC):

    @abstractmethod
    async def create_transaction(self, subscribe_type: Subscribe, current_user: User) -> Transaction:
        pass

    @abstractmethod
    async def create_subscribe(self, transaction: Transaction) -> None:
        pass

    @abstractmethod
    async def update_transaction(self, payment: Payment) -> Transaction:
        pass

    @abstractmethod
    async def update_subscribe(self, subscribe: Subscribe) -> None:
        pass

    @abstractmethod
    async def create_refund(self, payment: Payment, transaction: Transaction) -> None:
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
            logger.info(f'Subscribe create successful')
        except sqlalchemy.exc.IntegrityError:
            logger.error('Duplicate transaction_id')
        # TODO: Add kafka producer to AUTH

    async def create_refund(self, payment: Payment, transaction: Transaction) -> None:
        refund = Refund(
            transaction_id=transaction.id,
            aggregator_id=payment.id,
            amount=payment.amount,
            status=payment.status,
            failed_reason=payment.failed_reason
        )
        try:
            self.session.add(refund)
            await self.session.flush()
        except sqlalchemy.exc.IntegrityError:
            logger.error('Duplicate transaction_id')
        # TODO: Add kafka producer to AUTH

    async def update_subscribe(self, subscribe: Subscribe) -> None:
        new_end_date = subscribe.end_date + relativedelta(months=+1)
        subscribe.end_date = new_end_date

    async def get_subscribers(self) -> list[Subscribe]:
        query = select(Subscribe).where(
            Subscribe.end_date.cast(Date) == date.today()
        ).options(selectinload(Subscribe.subscribe_type), selectinload(Subscribe.transaction))
        queryset = await self.session.execute(query)
        subscribes = queryset.scalars().all()
        return subscribes

    async def update_transaction(self, payment: Payment) -> Transaction:
        query = await self.session.execute(select(Transaction).where(
            Transaction.aggregator_id == str(payment.id)
        ))
        transaction = query.scalar()
        transaction.status = payment.status
        transaction.failed_reason = payment.failed_reason
        transaction.card_4_numbers = payment.card
        return transaction


async def get_db(session: AsyncSession = Depends(get_session)) -> AlchemyDatabase:
    return AlchemyDatabase(session)
