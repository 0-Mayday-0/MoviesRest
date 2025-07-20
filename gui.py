from restapi import authorize, get_movies

import asyncio
from asyncio import Task
from collections.abc import Coroutine

from kivy.app import App as kvApp
from kivy.uix.gridlayout import GridLayout as kvGridLayout
from kivy.uix.button import Button as kvButton
from kivy.properties import ColorProperty

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


class ShowerWidget(kvGridLayout):
    def __init__(self, movies: Movies):
        super(ShowerWidget, self).__init__()
        self.movies = movies
        self.colors: dict[str, list[float]] = {"Not Started": [222/255, 30/255, 30/255, 1], #red 0
                                               "Watching": [233/255, 138/255, 0, 1], #orange 1
                                               "Watched": [97/255, 220/255, 62/255, 1] #green 2
                                                }

        self.cols: int = 3
        self.rows: int = 10
        self.max_buttons_per_page: int = self.cols * self.rows
        self.buttons_list: list[kvButton] = []

        self.functional_buttons= [kvButton(text="Next Page", on_press=self.next_page),
                                  kvButton(text="Previous Page", on_press=self.previous_page)]

        self.offset: int = 0

    async def buttons(self):
        self.movies: dict[str, tuple[str, str]] = await self.movies.fetch_spreadsheet()

        print(self.movies)

        self.buttons_list = [kvButton(text=f'{k}\n{v[1]}', background_color=self.colors[v[0]]) for k, v in self.movies.items()]

        for j in self.functional_buttons:
            self.add_widget(j)

        for i in self.buttons_list:
            self.add_widget(i)

    def next_page(self, widget):
        self.offset += self.max_buttons_per_page

    def previous_page(self, widget):
        self.current_page -= self.max_buttons_per_page
        

class ShowerApp(kvApp):
    def __init__(self, movies):
        self.movies = movies
        self.widget_instance: ShowerWidget = ShowerWidget(self.movies)
        super(ShowerApp, self).__init__()

    def build(self):
        return self.widget_instance

    async def creates(self):
        await self.widget_instance.buttons()
        self.build()

async def main():
    movies_obj: Movies = Movies()
    app = ShowerApp(movies_obj)
    await app.creates()
    app.run()



if __name__ == '__main__':
    asyncio.run(main())