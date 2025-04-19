from urllib.parse import urlencode
import asyncio

from utils.stremio import StremioStreamManager
from .main import get_movie_audios, get_series_audios
from .sources import warezcdn_stream

HOSTS = [
    "basseqwevewcewcewecwcw.xyz",
]


async def movie_streams(imdb: str, use_local_proxy: bool = False):
    audio_list = await get_movie_audios(imdb)
    tasks = []
    for audio in audio_list:
        for server in audio["servers"].split(","):
            if server == "mixdrop":
                continue
            if server == "warezcdn":
                tasks.append(warezcdn_stream(imdb, "filme", audio))

    stream_info_list = await asyncio.gather(*tasks)
    streams = StremioStreamManager()
    if not use_local_proxy:
        for stream_info in stream_info_list:
            streams.add_stream(stream_info.name, stream_info.title, stream_info.url, False, stream_info.headers)
    else:
        for stream_info in stream_info_list:
            query = urlencode({"url": stream_info.url, "headers": stream_info.headers})
            streams.add_stream(stream_info.name, stream_info.title, f"https://127.0.0.1:6222/proxy/?{query}")

    return streams.to_list()


async def series_stream(imdb: str, season: int, episode: int, use_local_proxy: bool = False):
    pass
