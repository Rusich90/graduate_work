import uuid

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import SmallInteger
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from db.config import Base


class SubscribeType(Base):
    __tablename__ = "subscribe_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(SmallInteger)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, unique=True, nullable=False)
    aggregator_id = Column(UUID(as_uuid=True), unique=True, nullable=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    subscribe_type_id = Column(Integer, ForeignKey("subscribe_types.id"), nullable=False)
    subscribe_type = relationship("SubscribeType", backref=backref("transactions"))
    amount = Column(Float)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False)
    failed_reason = Column(String, nullable=True, default=None)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())
    card_4_numbers = Column(SmallInteger)


class Subscribe(Base):
    __tablename__ = "subscribes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), unique=True, nullable=False)
    transaction = relationship("Transaction", backref=backref("subscribes"))
    subscribe_type_id = Column(Integer, ForeignKey("subscribe_types.id"), nullable=False)
    subscribe_type = relationship("SubscribeType", backref=backref("subscribes"))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    auto_renewal = Column(Boolean, default=True)
