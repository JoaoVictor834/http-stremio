# functions to get stremio formated streams for movies and series

from urllib.parse import urlencode

from utils.stremio import StremioStreamManager
from .main import get_media_pages, get_sources, get_epiosode_url
from .sources import streamtape_stream

HOSTS = [
    "streamtape.com",
]


async def movie_streams(imdb: str, use_local_proxy: bool = False):
    try:
        pages = await get_media_pages(imdb)
    except:
        return []

    streams = StremioStreamManager()
    if "dub" in pages.keys():
        # get list of links to every avaliable source
        dub_sources = await get_sources(f"{pages['dub']}?area=online")

        # extract stream links from every source
        try:
            stream_info = await streamtape_stream(dub_sources["streamtape"])
            stream = stream_info.url
            headers = stream_info.headers

            if not use_local_proxy:
                streams.add_stream("Pobreflix", "Streamtape (DUB)", stream, False, headers)
            else:
                query = urlencode({"url": stream, "headers": headers})
                streams.add_stream("Pobreflix", "Streamtape (DUB)", f"https://127.0.0.1:6222/proxy/?{query}")
        except:
            pass

    if "leg" in pages.keys():
        # get list of links to every avaliable source
        leg_sources = await get_sources(f"{pages['leg']}?area=online")

        # extract stream links from every source
        try:
            stream_info = await streamtape_stream(leg_sources["streamtape"])
            stream = stream_info.url
            headers = stream_info.headers

            if not use_local_proxy:
                streams.add_stream("Pobreflix", "Streamtape (LEG)", stream, False, headers)
            else:
                query = urlencode({"url": stream, "headers": headers})
                streams.add_stream("Pobreflix", "Streamtape (LEG)", f"https://127.0.0.1:6222/proxy/?{query}")
        except:
            pass

    # format as a stremio json
    return streams.to_list()


async def series_stream(imdb: str, season: int, episode: int, use_local_proxy: bool = False):
    try:
        pages = await get_media_pages(imdb)
    except:
        return []

    streams = StremioStreamManager()
    if "dub" in pages.keys():
        # get list of links to every avaliable source
        episode_url = await get_epiosode_url(pages["dub"], season, episode)
        if episode_url is not None:
            dub_sources = await get_sources(episode_url)

            # extract stream links from every source
            try:
                stream_info = await streamtape_stream(dub_sources["streamtape"])
                stream = stream_info.url
                headers = stream_info.headers

                if not use_local_proxy:
                    streams.add_stream("Pobreflix", "Streamtape (DUB)", stream, False, headers)
                else:
                    query = urlencode({"url": stream, "headers": headers})
                    streams.add_stream("Pobreflix", "Streamtape (DUB)", f"https://127.0.0.1:6222/proxy/?{query}")
            except:
                pass

    if "leg" in pages.keys():
        # get list of links to every avaliable source
        episode_url = await get_epiosode_url(pages["leg"], season, episode)
        if episode_url is not None:
            leg_sources = await get_sources(episode_url)

            # extract stream links from every source
            try:
                stream_info = await streamtape_stream(leg_sources["streamtape"])
                stream = stream_info.url
                headers = stream_info.headers

                if not use_local_proxy:
                    streams.add_stream("Pobreflix", "Streamtape (LEG)", stream, False, headers)
                else:
                    query = urlencode({"url": stream, "headers": headers})
                    streams.add_stream("Pobreflix", "Streamtape (LEG)", f"https://127.0.0.1:6222/proxy/?{query}")
            except:
                pass

    return streams.to_list()
