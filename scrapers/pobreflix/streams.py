# functions to get stremio formated streams for movies and series

from utils.stremio import StremioStreamManager
from .main import get_media_pages, get_sources, get_epiosode_url
from . import sources


async def movie_streams(imdb: str):
    pages = await get_media_pages(imdb)

    streams = StremioStreamManager()
    if "dub" in pages.keys():
        # get list of links to every avaliable source
        dub_sources = await get_sources(f"{pages['dub']}?area=online")

        # extract stream links from every source
        try:
            streamtape = await sources.streamtape(dub_sources["streamtape"])
            streams.add_stream("Pobreflix", "Streamtape (DUB)", streamtape["url"], False, streamtape["headers"])
        except:
            pass

    if "leg" in pages.keys():
        # get list of links to every avaliable source
        leg_sources = await get_sources(f"{pages['leg']}?area=online")

        # extract stream links from every source
        try:
            streamtape = await sources.streamtape(leg_sources["streamtape"])
            streams.add_stream("Pobreflix", "Streamtape (LEG)", streamtape["url"], False, streamtape["headers"])
        except:
            pass

    # format as a stremio json
    return streams.to_list()


async def series_stream(imdb: str, season: int, episode: int):
    pages = await get_media_pages(imdb)

    streams = StremioStreamManager()
    if "dub" in pages.keys():
        # get list of links to every avaliable source
        episode_url = await get_epiosode_url(pages["dub"], season, episode)
        if episode_url is not None:
            dub_sources = await get_sources(episode_url)

            # extract stream links from every source
            try:
                streamtape = await sources.streamtape(dub_sources["streamtape"])
                streams.add_stream("Pobreflix", "Streamtape (DUB)", streamtape["url"], False, streamtape["headers"])
            except:
                pass

    if "leg" in pages.keys():
        # get list of links to every avaliable source
        episode_url = await get_epiosode_url(pages["leg"], season, episode)
        if episode_url is not None:
            leg_sources = await get_sources(episode_url)

            # extract stream links from every source
            try:
                streamtape = await sources.streamtape(leg_sources["streamtape"])
                streams.add_stream("Pobreflix", "Streamtape (LEG)", streamtape["url"], False, streamtape["headers"])
            except:
                pass

    return streams.to_list()
