from restapi import authorize, get_movies
from asyncio import Task
import asyncio

class MovieFetcher:
    def __init__(self):
        authorize()
        self.movies: dict[str, str] = {}

    async def fetch(self):
        self.movies: dict[str, tuple[str, str]] = await get_movies()
        return self.movies

class Movies:
    def __init__(self):
        self.movies: dict[str, str] = {}

    @staticmethod
    async def fetch_spreadsheet():
        fetcher = MovieFetcher()
        movies_task: Task[dict[str, tuple[str, str]]] = asyncio.create_task(fetcher.fetch())

        movies_status: dict[str, tuple[str, str]] = await movies_task

        return movies_status