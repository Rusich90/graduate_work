from abc import ABC, abstractmethod
from typing import Dict, Optional

from core import settings
from db.config import Base
# from db.config import async_session

class AbstractDatabase(ABC):

    @abstractmethod
    async def get_all(self, cls):
        pass


class AlchemyDatabase(AbstractDatabase):
    def __init__(self):
        self.db = self.get_db()

    async def get_all(self, cls: Base):
        pass

    async def get_db(self):
        async with self.session() as session:
            async with session.begin():
                yield session
