from functools import lru_cache
from typing import List, Optional

from fastapi import Depends

from db.database import AbstractDataBase
from db.elastic import get_elastic
from schemas.film import Film
from schemas.genre import Genre
from services.service import Service


class GenreService(Service):

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        genre = await self.database.get('genres', genre_id)
        if genre:
            genre = Genre(**genre['_source'])
        return genre

    async def get_all_by_index(self, path: str, size: int, search: Optional[str],
                               search_after: Optional[str]) -> Optional[List[Genre]]:
        genres = await self._get_all(path, 'genres', size, search, search_after)
        return [Genre(**genre['_source']) for genre in genres['hits']['hits']]

    async def get_movies(self, path: str, genre_id: str, size: int, search_after: Optional[str],
                         detail: Optional[bool] = False) -> Optional[List[Film]]:
        body = {
            "query": {
                "nested": {
                    "path": "genres",
                    "query": {
                        "bool": {
                            "must": [{"match": {"genres.id": genre_id}}]
                        }
                    }
                }
            }
        }
        movies = await self._get_movies(path, size, body, search_after)
        return [Film(**movie['_source']) for movie in movies['hits']['hits']]


@lru_cache()
def get_genre_service(db: AbstractDataBase = Depends(get_elastic)) -> GenreService:
    return GenreService(db)
