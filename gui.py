from restapi import authorize, get_movies

from icecream import ic

from itertools import batched

import asyncio
from asyncio import Task
from collections.abc import Coroutine

from kivy.app import App as kvApp
from kivy.uix.gridlayout import GridLayout as kvGridLayout
from kivy.uix.pagelayout import PageLayout as kvPageLayout
from kivy.uix.button import Button as kvButton
from kivy.properties import ColorProperty

from movie_objects import Movies


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
        self.buttons_list: list[kvButton] = []
        self.divided_buttons: list[tuple[kvButton, ...]] = []

        self.functional_buttons= [kvButton(text="Previous Page", on_press=self.previous_page),
                                  kvButton(text="Next Page", on_press=self.next_page)]

        self.max_buttons_per_page: int = (self.cols * self.rows) - len(self.functional_buttons)

        self.offset: int = 0

    async def buttons(self):
        self.movies: dict[str, tuple[str, str]] = await self.movies.fetch_spreadsheet()

        ic(self.movies)

        self.buttons_list = [kvButton(text=f'{k}\n{v[1]}', background_color=self.colors[v[0]]) for k, v in self.movies.items()]

        self.divided_buttons = list(batched(self.buttons_list, self.max_buttons_per_page))
        ic(len(self.divided_buttons[0]))

        for j in self.functional_buttons:
            self.add_widget(j)

        counter = 0

        while counter < self.max_buttons_per_page:
            self.add_widget(self.buttons_list[counter])
            counter += 1
        ic(len(self.children))

    def destroy_next(self):
        to_remove = self.buttons_list[self.offset : self.offset + self.max_buttons_per_page]

        self.clear_widgets(to_remove)

        for j in self.functional_buttons:
            self.remove_widget(j)
        ic(len(self.children))

    def destroy_previous(self):
        to_remove = self.buttons_list[self.offset + self.max_buttons_per_page : self.offset : -1]

        self.clear_widgets(to_remove)
        ic(len(self.children))

        #for i in to_remove:
            #ic(i)
            #if self.offset + self.max_buttons_per_page < len(self.buttons_list):
                #self.remove_widget(i)

    def rebuild_from_offset_next(self):
        to_add = self.buttons_list[self.offset : self.offset + self.max_buttons_per_page]

        for j in self.functional_buttons:
            self.add_widget(j)

        for i in to_add:
            self.add_widget(i)


    def rebuild_from_offset_previous(self):
        to_add = self.buttons_list[self.offset + self.max_buttons_per_page : self.offset : -1]

        ic(self.offset)

        for i in to_add:
            self.add_widget(i)



    def next_page(self, widget):
        if self.offset < self.max_buttons_per_page -1:
            self.destroy_next()
            self.offset += self.max_buttons_per_page
            self.rebuild_from_offset_next()
            ic(len(self.children))
        else:
            ic("no more")

    def previous_page(self, widget):
        if self.offset >= self.max_buttons_per_page -1 and self.offset != 0:
            self.offset -= self.max_buttons_per_page
            self.destroy_next()
            self.rebuild_from_offset_previous()
        else:
            ic(self.max_buttons_per_page)
            ic(self.offset)
            ic("no more")





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