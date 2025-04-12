# general functions and classes needed to scrape the site

from urllib.parse import urljoin
import asyncio
import typing
import re

import requests

from utils.imdb import IMDB
from utils.stremio import StremioStreamManager
from .sources import REDECANAIS_URL
from .utils import to_kebab_case

MOVIE_LIST = {}
SERIES_LIST = {}


def parse_media_lists():
    """Turn list of movies and list of series into dicts grouped by initial letters"""
    movie_list_response = requests.get(urljoin(REDECANAIS_URL, "mapafilmes.html"))
    series_list_response = requests.get(urljoin(REDECANAIS_URL, "mapa.html"))

    # iterate through every line of movies html searching for urls
    list_started = False
    for line in movie_list_response.iter_lines():
        line = str(line)
        # wait for the beggining of the list to be reached
        if not list_started:
            if "<b>Filmes</b>" in line:
                list_started = True

        else:
            url = re.findall(r"href *= *\"(.+?)\"", line)
            if url:
                url = url[0]

                # append url to the list corresponding to its first letter
                first_letter = url[1]
                if first_letter.isalpha():
                    try:
                        MOVIE_LIST[first_letter].append(url)
                    except KeyError:
                        MOVIE_LIST.update({first_letter: []})
                        MOVIE_LIST[first_letter].append(url)
                else:
                    try:
                        MOVIE_LIST["-"].append(url)
                    except KeyError:
                        MOVIE_LIST.update({"-": []})
                        MOVIE_LIST["-"].append(url)

    # iterate through every line of series html searching for urls
    list_started = False
    for line in series_list_response.iter_lines():
        line = str(line)
        # wait for the beggining of the list to be reached
        if not list_started:
            if "<b>Animes</b>" in line:
                list_started = True

        else:
            url = re.findall(r"href *= *\"(.+?)\"", line)
            if url:
                url = url[0]

                # append url to the list corresponding to its first letter
                first_letter = url[8]
                if first_letter.isalpha():
                    try:
                        SERIES_LIST[first_letter].append(url)
                    except KeyError:
                        SERIES_LIST.update({first_letter: []})
                        SERIES_LIST[first_letter].append(url)
                else:
                    try:
                        SERIES_LIST["-"].append(url)
                    except KeyError:
                        SERIES_LIST.update({"-": []})
                        SERIES_LIST["-"].append(url)


async def get_media_pages(imdb: str, type: typing.Literal["movie", "series"]) -> dict:
    # get information about the target media
    info = await IMDB.get(imdb, "pt")
    title = to_kebab_case(info.title)
    year = str(info.year)
    first_char = title[0] if title[0].isalpha() else "-"

    # parse lists used on the search if not parsed yet
    if not (MOVIE_LIST and SERIES_LIST):
        parse_media_lists()

    # search for the target media
    media_pages = {}
    match type:
        case "movie":
            for url in MOVIE_LIST[first_char]:
                if title in url and year in url:
                    if "legendado" in url:
                        media_pages.update({"leg": urljoin(REDECANAIS_URL, url)})
                    else:
                        media_pages.update({"dub": urljoin(REDECANAIS_URL, url)})

        case "series":
            pass

    return media_pages
