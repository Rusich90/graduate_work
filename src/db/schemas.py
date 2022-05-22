from pydantic import BaseModel


class Subscription(BaseModel):
    id: int
    name: str
    price: int

    class Config:
        orm_mode = True
