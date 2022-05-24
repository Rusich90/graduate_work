import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class CustomModel(BaseModel):

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps

class Subscription(CustomModel):
    id: int
    name: str
    price: int

    class Config:
        orm_mode = True


class TransactionCreate(CustomModel):
    subscribe_type_id: int