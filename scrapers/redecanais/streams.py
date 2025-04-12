# functions to get stremio formated streams for movies and series
from urllib.parse import urlencode

from utils.stremio import StremioStreamManager
from .main import get_movie_pages, get_series_pages
from .sources import get_video_player_url, get_download_page_url, get_stream_url


async def movie_streams(imdb: str, use_local_proxy: bool = False):
    try:
        pages = await get_movie_pages(imdb)
    except:
        return []

    streams = StremioStreamManager()
    if "dub" in pages.keys():
        # get video stream
        video_player_url = get_video_player_url(pages["dub"])
        download_page_url = get_download_page_url(video_player_url)
        stream = get_stream_url(download_page_url)

        if not use_local_proxy:
            # create formated stream json
            headers = {"Referer": download_page_url}
            streams.add_stream("Redecanais", "Redecanais (DUB)", stream, False, headers=headers)
        else:
            # create formated stream json using proxy
            headers = {"Referer": download_page_url}
            query = urlencode({"url": stream, "headers": headers})
            streams.add_stream("Redecanais", "Redecanais (DUB)", f"https://127.0.0.1:6222/proxy/?{query}")

    if "leg" in pages.keys():
        # get video stream
        video_player_url = get_video_player_url(pages["leg"])
        download_page_url = get_download_page_url(video_player_url)
        stream = get_stream_url(download_page_url)

        if not use_local_proxy:
            # create formated stream json
            headers = {"Referer": download_page_url}
            streams.add_stream("Redecanais", "Redecanais (LEG)", stream, False, headers=headers)

        else:
            # create formated stream json using proxy
            headers = {"Referer": download_page_url}
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
        video_player_url = get_video_player_url(pages["dub"])
        download_page_url = get_download_page_url(video_player_url)
        stream = get_stream_url(download_page_url)

        if not use_local_proxy:
            # create formated stream json
            headers = {"Referer": download_page_url}
            streams.add_stream("Redecanais", "Redecanais (DUB)", stream, False, headers=headers)
        else:
            # create formated stream json using proxy
            headers = {"Referer": download_page_url}
            query = urlencode({"url": stream, "headers": headers})
            streams.add_stream("Redecanais", "Redecanais (DUB)", f"https://127.0.0.1:6222/proxy/?{query}")

    if "leg" in pages.keys():
        # get video stream
        video_player_url = get_video_player_url(pages["leg"])
        download_page_url = get_download_page_url(video_player_url)
        stream = get_stream_url(download_page_url)

        if not use_local_proxy:
            # create formated stream json
            headers = {"Referer": download_page_url}
            streams.add_stream("Redecanais", "Redecanais (LEG)", stream, False, headers=headers)

        else:
            # create formated stream json using proxy
            headers = {"Referer": download_page_url}
            query = urlencode({"url": stream, "headers": headers})
            streams.add_stream("Redecanais", "Redecanais (LEG)", f"https://127.0.0.1:6222/proxy/?{query}")

    return streams.to_list()
