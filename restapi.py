from dotenv import load_dotenv
from os import getenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import asyncio
from asyncio import Task
from collections.abc import Coroutine

load_dotenv('./secret/uris.env')

async def authorize() -> gspread.Worksheet | str:
    #baseuri: str = getenv('BASE')
    #spid: str = getenv('SPID')
    #path_get = getenv('GET')
    #path_get: str = f"{baseuri}{path_get.format(spid=spid)}"

    credentials_file: str = getenv("CREDS")
    access: list[str] = [getenv('ACCESS_SHEETS'), getenv('ACCESS_DRIVE')]
    book: str = getenv('WORKBOOK')

    credentials: ServiceAccountCredentials = (ServiceAccountCredentials
                                              .from_json_keyfile_name(credentials_file, scopes=access))

    try:
        # noinspection PyTypeChecker
        file_coroutine: Coroutine[None, ServiceAccountCredentials, gspread.Client] | gspread.Client = \
            await asyncio.to_thread(gspread.authorize, credentials)

        print("Authorized gspread")


        file: gspread.Spreadsheet | str = file_coroutine.open(book)

    except gspread.exceptions.APIError as e:
        return f"{e.response}: An error has occurred"

    return file.sheet1

async def get_movies() -> dict[str, tuple[str, str]]:
    sheets_task: Task[gspread.Worksheet | str] = asyncio.create_task(authorize())

    movie_col: int = 1
    season_col: int = 2
    status_col: int = 4
    header: str = "Series"

    worksheet: gspread.Worksheet = await sheets_task

    movies = [movie for movie in worksheet.col_values(movie_col)]
    seasons = [season for season in worksheet.col_values(season_col)]
    statuses = [status for status in worksheet.col_values(status_col)]

    del movies[0], seasons[0], statuses[0]

    movies_return = {}

    for index, movie in enumerate(movies):
        movies_return[movie] = (statuses[index], seasons[index])

    #movies: dict[str, str] = {movie: status for movie, status in zip(worksheet.col_values(movie_col),
                                                                    # worksheet.col_values(status_col))}
    #del movies[header] #remove the sheet's headers, only movies/series

    # noinspection PyTypeChecker
    # movies_return
    return movies_return

async def main() -> None:
    movies: dict[str, tuple[str, str]] = await get_movies()

    print(movies)

if __name__ == "__main__":
    asyncio.run(main())