# functions to get stremio formated streams for movies and series
from urllib.parse import urlencode

from utils.stremio import StremioStreamManager
from .main import get_media_pages
from .sources import get_video_player_url, get_download_page_url, get_stream_url


async def movie_streams(imdb: str):
    pages = await get_media_pages(imdb, "movie")

    streams = StremioStreamManager()
    if "dub" in pages.keys():
        # get video stream
        video_player_url = get_video_player_url(pages["dub"])
        download_page_url = get_download_page_url(video_player_url)
        stream = get_stream_url(download_page_url)

        # create formated stream json
        headers = {"Referer": download_page_url}
        streams.add_stream("Redecanais", "Redecanais (DUB)", stream, False, headers=headers)

    if "leg" in pages.keys():
        # get video stream
        video_player_url = get_video_player_url(pages["leg"])
        download_page_url = get_download_page_url(video_player_url)
        stream = get_stream_url(download_page_url)

        # create formated stream json
        headers = {"Referer": download_page_url}
        streams.add_stream("Redecanais", "Redecanais (LEG)", stream, False, headers=headers)

    return streams.to_list()


async def series_stream(imdb: str, season: int, episode: int):
    pass
