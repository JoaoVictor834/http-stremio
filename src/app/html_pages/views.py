import json
import os

import aiohttp
import aiofiles
from jinja2 import Environment, FileSystemLoader
from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse

from src.scrapers import redecanais
from . import constants

templates = Environment(loader=FileSystemLoader(constants.TEMPLATES_DIR))


async def index():
    async with aiofiles.open("./selected-media.json", "r", encoding="utf8") as f:
        selected_media = json.loads(await f.read())

    data = {
        "selected_movies": selected_media["movies"],
        "selected_series": selected_media["series"],
    }

    template = templates.get_template("index.html")
    return HTMLResponse(template.render(data))


async def movie_info(id: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://v3-cinemeta.strem.io/meta/movie/{id}.json") as response:
            series_data = await response.json()

    # get movie variables
    name = series_data["meta"]["name"]
    background = series_data["meta"]["background"]
    poster = series_data["meta"]["poster"]
    logo = series_data["meta"]["logo"]

    # render template
    template = templates.get_template("movie.html")
    data = {
        "name": name,
        "logo": logo,
        "poster": poster,
        "background": background,
        "id": id,
    }
    return HTMLResponse(template.render(data))


async def series_info(id: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://v3-cinemeta.strem.io/meta/series/{id}.json") as response:
            series_data = await response.json()

    # create a dict for every season
    seasons = {}
    for video in series_data["meta"]["videos"]:
        if video["season"] == 0:
            continue

        episode = {
            "number": video["number"],
            "title": video["name"],
            "image": video["thumbnail"],
        }

        try:
            seasons[video["season"]]["episodes"].append(episode)

        except KeyError:
            seasons.update({video["season"]: {"number": video["season"], "episodes": []}})
            seasons[video["season"]]["episodes"].append(episode)

    # convert seasons dict to a list
    seasons = [seasons[key] for key in seasons.keys()]

    # get remaining series variables
    name = series_data["meta"]["name"]
    background = series_data["meta"]["background"]
    poster = series_data["meta"]["poster"]
    logo = series_data["meta"]["logo"]

    # render template
    template = templates.get_template("series.html")
    data = {
        "seasons": seasons,
        "name": name,
        "logo": logo,
        "poster": poster,
        "background": background,
        "id": id,
    }
    return HTMLResponse(template.render(data))


async def watch_movie(id: str, proxy_url: str, cache_url: str, user_agent: str):
    # get stream
    streams = await redecanais.movie_streams(id, proxy_url=proxy_url, cache_url=cache_url)
    stream = streams[0]["url"]

    # return raw stream if on android 4.2.2
    if "Android 4.2.2" in user_agent:
        return RedirectResponse(stream)

    # render player template
    template = templates.get_template("player.html")
    data = {"url": stream}
    return HTMLResponse(template.render(data))


async def watch_series(id: str, season: int, episode: int, proxy_url: str, cache_url: str, user_agent: str):
    # get stream
    streams = await redecanais.series_stream(id, season, episode, proxy_url=proxy_url, cache_url=cache_url)
    stream = streams[0]["url"]

    # return raw stream if on android 4.2.2
    if "Android 4.2.2" in user_agent:
        return RedirectResponse(stream)

    # render player template
    template = templates.get_template("player.html")
    data = {"url": stream}
    return HTMLResponse(template.render(data))
