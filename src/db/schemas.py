from datetime import date
from datetime import datetime
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


class Transaction(CustomModel):
    id: UUID
    description: str
    amount: int
    status: str
    created_at: datetime
    failed_reason: str = None
    card_4_numbers: int

    class Config:
        orm_mode = True


class TransactionCreate(CustomModel):
    subscribe_type_id: int


class OkBody(BaseModel):
    detail: str
