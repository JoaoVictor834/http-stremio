# functions to get stremio formated streams for movies and series
from urllib.parse import urlencode

from utils.stremio import StremioStreamManager
from .main import get_movie_pages, get_series_pages
from .sources import player_stream

HOSTS = [
    "redecanais.gs",
]


async def movie_streams(imdb: str, use_local_proxy: bool = False):
    try:
        pages = await get_movie_pages(imdb)
    except:
        return []

    streams = StremioStreamManager()
    if "dub" in pages.keys():
        # get video stream
        stream_info = await player_stream(pages["dub"])
        stream = stream_info.url
        headers = stream_info.headers

        if not use_local_proxy:
            # create formated stream json
            streams.add_stream("Redecanais", "Redecanais (DUB)", stream, False, headers=headers)
        else:
            # create formated stream json using proxy
            query = urlencode({"url": stream, "headers": headers})
            streams.add_stream("Redecanais", "Redecanais (DUB)", f"https://127.0.0.1:6222/proxy/?{query}")

    if "leg" in pages.keys():
        # get video stream
        stream_info = await player_stream(pages["leg"])
        stream = stream_info.url
        headers = stream_info.headers

        if not use_local_proxy:
            # create formated stream json
            streams.add_stream("Redecanais", "Redecanais (LEG)", stream, False, headers=headers)

        else:
            # create formated stream json using proxy
            query = urlencode({"url": stream, "headers": headers})
            streams.add_stream("Redecanais", "Redecanais (LEG)", f"https://127.0.0.1:6222/proxy/?{query}")

    return streams.to_list()


async def series_stream(imdb: str, season: int, episode: int, use_local_proxy: bool = False):
    try:
        pages = await get_series_pages(imdb, season, episode)
    except:
        return []

    streams = StremioStreamManager()
    if "dub" in pages.keys():
        # get video stream
        stream_info = await player_stream(pages["dub"])
        stream = stream_info.url
        headers = stream_info.headers

        if not use_local_proxy:
            # create formated stream json
            streams.add_stream("Redecanais", "Redecanais (DUB)", stream, False, headers=headers)
        else:
            # create formated stream json using proxy
            query = urlencode({"url": stream, "headers": headers})
            streams.add_stream("Redecanais", "Redecanais (DUB)", f"https://127.0.0.1:6222/proxy/?{query}")

    if "leg" in pages.keys():
        # get video stream
        stream_info = await player_stream(pages["leg"])
        stream = stream_info.url
        headers = stream_info.headers

        if not use_local_proxy:
            # create formated stream json
            streams.add_stream("Redecanais", "Redecanais (LEG)", stream, False, headers=headers)

        else:
            # create formated stream json using proxy
            query = urlencode({"url": stream, "headers": headers})
            streams.add_stream("Redecanais", "Redecanais (LEG)", f"https://127.0.0.1:6222/proxy/?{query}")

    return streams.to_list()
