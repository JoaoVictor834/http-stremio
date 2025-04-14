# general functions and classes needed to scrape the site

from urllib.parse import urljoin
import asyncio
import typing
import re

from bs4 import BeautifulSoup
import aiohttp

from utils.imdb import IMDB
from .sources import REDECANAIS_URL
from .utils import to_kebab_case
from .decoders import decode_from_response

MOVIE_LIST = {}
SERIES_LIST = {}


async def parse_media_lists():
    """Turn list of movies and list of series into dicts grouped by initial letters"""
    print("parse_media_lists")
    async with aiohttp.ClientSession() as session:
        tasks = [
            session.get(urljoin(REDECANAIS_URL, "mapafilmes.html")),
            session.get(urljoin(REDECANAIS_URL, "mapa.html")),
        ]

        results = await asyncio.gather(*tasks)
        movie_list_response: aiohttp.ClientResponse = results[0]
        series_list_response: aiohttp.ClientResponse = results[1]

        # iterate through every line of movies html searching for urls
        list_started = False
        movie_list_text = await movie_list_response.text()
        for line in movie_list_text.split("\n"):
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
        series_list_text = await series_list_response.text()
        for line in series_list_text.split("\n"):
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

        movie_list_response.release()
        series_list_response.release()


# TODO: update it to work with pages that don't reset the episode number on each season
async def get_series_pages(imdb: str, season: int, episode: int):
    print("get_series_pages")
    info = await IMDB.get(imdb, "pt")
    title = to_kebab_case(info.title)
    first_char = title[0] if title[0].isalpha() else "-"

    # parse lists used on the search if not parsed yet
    if not (MOVIE_LIST and SERIES_LIST):
        await parse_media_lists()

    # run through the list of series searching for urls that contains the target title
    matches = []
    for url in SERIES_LIST[first_char]:
        if title in url:
            matches.append(url)

    # get the match with the lowest amount of chars to remove series with bigger titles that contain the target title
    page_url = matches[0]
    for match in matches:
        if len(match) < len(page_url):
            page_url = match

    page_url = urljoin(REDECANAIS_URL, page_url)
    async with aiohttp.ClientSession() as session:
        async with session.get(page_url) as response:
            html = BeautifulSoup(await decode_from_response(response), "html.parser")

    # get the html element containing all episodes
    p_list = html.find_all("p")
    episodes_html = ""
    for p in p_list:
        p: BeautifulSoup
        if len(p.text) > len(episodes_html):
            episodes_html = p.prettify()

    # search for the season and episode sequentially
    season_found = False
    episode_found = False
    episode_urls = []
    episode_audios = []
    episode_pages = {}
    for line in episodes_html.splitlines():
        # search for the target season
        if not season_found:
            if "Temporada" in line and str(season) in line:
                season_found = True
                continue

        # search for the target episode
        elif not episode_found:
            if "Ep" in line and str(episode) in line:
                episode_found = True
                continue

        # search for the episode pages urls
        else:
            url = re.findall(r"href *= *\"(.+?)\"", line)
            if url:
                url = urljoin(REDECANAIS_URL, url[0])
                episode_urls.append(url)

            # mark episode as dub or leg
            elif "Legendado" in line:
                episode_audios.append("leg")
            elif "Assistir" in line or "Dublado" in line:
                episode_audios.append("dub")

            # break loop if a new episode or season or the max amount of streams is reached
            elif "Ep" in line and str(episode + 1) in line:
                break
            elif "Temporada" in line and str(season + 1) in line:
                break
            if len(episode_urls) >= 2:
                break

    # mount the pages dict
    for i, key in enumerate(episode_audios):
        episode_pages.update({key: episode_urls[i]})

    return episode_pages


async def get_movie_pages(imdb: str) -> dict:
    # get information about the target media
    info = await IMDB.get(imdb, "pt")
    title = to_kebab_case(info.title)
    year = str(info.year)
    first_char = title[0] if title[0].isalpha() else "-"

    # parse lists used on the search if not parsed yet
    if not (MOVIE_LIST and SERIES_LIST):
        await parse_media_lists()

    # search for the target media
    media_pages = {}
    for url in MOVIE_LIST[first_char]:
        if title in url and year in url:
            if "legendado" in url:
                media_pages.update({"leg": urljoin(REDECANAIS_URL, url)})
            else:
                media_pages.update({"dub": urljoin(REDECANAIS_URL, url)})

    return media_pages
