from abc import ABC, abstractmethod
from typing import Dict, Optional

from core import settings
from db.database import AbstractDataBase


class AbstractService(ABC):

    @abstractmethod
    def __init__(self, database):
        self.database = database
        self.expire = config.EXPIRE_TIME
        self.pagination = None
        self.count = None

    @abstractmethod
    async def set_pagination_and_count(self, doc: Dict, movies: bool = None):
        pass

    @abstractmethod
    async def get_by_id(self, record_id: str):
        pass

    @abstractmethod
    async def get_all_by_index(self, path: str, size: int, search: Optional[str], search_after: Optional[str]):
        pass

    @abstractmethod
    async def get_movies(self, path: str, record_id: str, size: int,
                         search_after: Optional[str]):
        pass


class Service(AbstractService):
    def __init__(self, database: AbstractDataBase):
        super().__init__(database)

    async def set_pagination_and_count(self, doc: Dict, movies: bool = None, score: bool = None) -> None:
        if len(doc['hits']['hits']) > 0:
            self.pagination = doc['hits']['hits'][-1]['_source']['id']
            if movies and score:
                self.pagination = f"{doc['hits']['hits'][-1]['_score']}_{self.pagination}"
            elif movies:
                self.pagination = f"{doc['hits']['hits'][-1]['_source']['imdb_rating']}_{self.pagination}"
        else:
            self.pagination = None
        self.count = doc['hits']['total']['value']

    async def get_by_id(self, record_id: str):
        raise NotImplementedError()

    async def get_all_by_index(self, path: str, size: int, search: Optional[str], search_after: Optional[str]):
        raise NotImplementedError()

    async def get_movies(self, path: str, record_id: str, size: int, search_after: Optional[str]):
        raise NotImplementedError()

    async def _get_all(self,
                       path: str,
                       index: str,
                       size: int,
                       search: Optional[str],
                       search_after: Optional[str]):
        param = {
            'index': index,
            'sort': ["imdb_rating:desc", "id:asc"] if index == 'movies' else 'id:asc',
            'size': size,
            'body': {}
        }

        if search and index == 'movies':
            param['body'] = {"query": {"match": {"title": search}}}
        elif search:
            param['body'] = {"query": {"match": {"name": search}}}

        if search_after:
            param['body']['search_after'] = search_after.split('_') if index == 'movies' else [search_after]

        movie = True if index == 'movies' else False

        records = await self.database.get_all(path, param)
        await self.set_pagination_and_count(records, movie)
        return records

    async def _get_movies(self,
                          path: str,
                          size: int,
                          body: Dict,
                          search_after: Optional[str] = None,
                          score: Optional[bool] = False):
        param = {
            "index": "movies",
            "sort": ["_score:desc" if score else "imdb_rating:desc", "id:asc"],
            "size": size,
            'body': body,
        }

        if search_after:
            param['body']['search_after'] = search_after.split('_')
        movies = await self.database.get_all(path, param)
        await self.set_pagination_and_count(movies, True, score)
        return movies

