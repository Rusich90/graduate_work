from abc import ABC
from abc import abstractmethod
from typing import Optional

import orjson
from aioredis import Redis

from core.settings import CacheSettings

config = CacheSettings()


class AbstractCache(ABC):

    @abstractmethod
    async def get(self, key: str) -> str:
        pass

    @abstractmethod
    async def set(self, key: str, data: str) -> None:
        pass


class RedisCache(AbstractCache):

    def __init__(self, session):
        self.expire = config.expire_time
        self.session = session

    async def get(self, key):
        data = await self.session.get(key)
        if not data:
            return None
        data = orjson.loads(data)
        return data

    async def set(self, key, data):
        await self.session.set(key, orjson.dumps(data), expire=self.expire)


cache: Optional[Redis] = None


async def get_cache() -> AbstractCache:
    return RedisCache(cache)
