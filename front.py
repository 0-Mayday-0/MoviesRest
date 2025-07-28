import asyncio
from asyncio import Task

import PySimpleGUI as sg

from itertools import batched

from screeninfo import get_monitors, Monitor

from movie_objects import Movies

def repack(widget, option):
    pack_info = widget.pack_info()
    pack_info.update(option)
    widget.pack(**pack_info)

class ShowerWindow(sg.Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.movies: Movies = Movies()
        self.layouts: list[list[sg.Column]] = []

        self.all_buttons: list[sg.Button] = []


        self.functional_buttons: list[sg.Button] = [sg.Button(button_text="Previous page"),
                                                    sg.Button(button_text="Next page")]


        self.button_pages: list[list[sg.Button]] = []

        self.colors: dict[str, str] = {"Not Started" : "White on Red",
                                        "Watching" : "Black on Yellow",
                                        "Watched" : "Black on Green"}
        self.max_buttons_per_page: int = 28


        self.current_page: int = 0


        self.cols: int = 6
        self.expand: bool = True

        self.title = kwargs["title"]

        self.movies = self.movies

    async def create_buttons(self) -> None:
        self.movies = await self.movies.fetch_spreadsheet()

        self.all_buttons = [sg.Button(button_text=f"{k}\n{v[1]}",
                                      button_color=self.colors[v[0]],
                                      expand_x=self.expand,
                                      expand_y=self.expand,
                                      pad=(25))
                            for k, v in self.movies.items()]

        self.button_pages = list(batched(self.all_buttons, self.max_buttons_per_page))



        for i, v in enumerate(self.button_pages):
            curr_layout = []
            for button in v:
                curr_layout.append(button)

            print(i)
            curr_layout = list(batched(curr_layout, self.cols))

            self.layouts.append(sg.Column(curr_layout, key=i, expand_x=self.expand, expand_y=self.expand))

        self.layout(rows=[self.functional_buttons] + [self.layouts])
        self.finalize()

        for i, v in enumerate(self.button_pages):
            if i == 0:
                continue
            self[self.current_page+i].update(visible=False)


    def next_page(self):

        try:
            if self.current_page + 1 == len(list(self.button_pages)):
                raise IndexError
            else:
                self[self.current_page].update(visible=False)
                self.current_page += 1
                print(list(self.button_pages))

            self[self.current_page].update(visible=True)
        except IndexError:
            print("No more pages")



    def previous_page(self):
        try:
            if self.current_page - 1 < 0:
                raise IndexError
            else:
                self[self.current_page].update(visible=False)
                self.current_page -= 1

            self[self.current_page].update(visible=True)
        except IndexError:
            print("No more pages")


async def main() -> None:
    monitors = get_monitors()

    for monitor in monitors:
        if not monitor.is_primary:
            continue
        else:
            window_size = (monitor.width, monitor.height)

    w = ShowerWindow(title="Hello World!",
                     size=window_size,
                     resizable=True)

    await w.create_buttons()

    w.maximize()

    while True:
        event, values = w.read()

        if event == sg.WIN_CLOSED:
            break

        if event == "Next page":
            w.next_page()

        if event == "Previous page":
            w.previous_page()

    w.close()

if __name__ == "__main__":
    asyncio.run(main())