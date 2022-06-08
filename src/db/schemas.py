from datetime import date
from datetime import datetime
from typing import Optional
from uuid import UUID

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class CustomModel(BaseModel):

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class SubscriptionTypeSchema(BaseModel):
    id: int
    name: str
    price: int

    class Config:
        orm_mode = True


class SubscriptionUpdateSchema(BaseModel):
    auto_renewal: bool


class SubscriptionBaseSchema(BaseModel):
    id: UUID
    auto_renewal: bool

    class Config:
        orm_mode = True


class SubscriptionSchema(SubscriptionBaseSchema):
    subscribe_type: SubscriptionTypeSchema
    end_date: date


class TransactionDetail(CustomModel):
    id: UUID
    description: str
    amount: int
    status: str
    created_at: datetime
    failed_reason: Optional[str]
    card_4_numbers: Optional[int]

    class Config:
        orm_mode = True


class TransactionCreate(CustomModel):
    subscribe_type_id: int


class TransactionRefund(CustomModel):
    transaction_id: UUID


class OkBody(BaseModel):
    detail: str


class Payment(BaseModel):
    id: UUID
    status: str
    amount: float
    confirmation_url: Optional[str]
    card: Optional[int]
    failed_reason: Optional[str]
