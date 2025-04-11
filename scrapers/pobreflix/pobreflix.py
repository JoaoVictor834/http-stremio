from urllib.parse import urljoin, urlencode
import asyncio

from bs4 import BeautifulSoup
import aiohttp

from imdb import IMDB
from scrapers.pobreflix.utils import stream_from_streamtape
from stremio import StremioStreamManager


BASE_URL = "https://pobreflixtv.love/"


class PobreflixResult:
    def __init__(self, title, year, audio, url):
        self.title = title
        self.year = year
        self.audio = audio.lower()
        self.url = url

    def __str__(self):
        return f"<title: {self.title} | year: {self.year} | audio: {self.audio} | url: {self.url}>"


async def search(search_term: str) -> list[PobreflixResult]:
    # search for its title on the site
    query_params = urlencode({"p": search_term})
    search_url = urljoin(BASE_URL, "pesquisar")
    search_url = f"{search_url}?{query_params}"

    async with aiohttp.ClientSession() as session:
        response = await session.get(search_url)
        if response.status != 200:
            msg = f"Unexpected status code when fetching page. Expected '200', got '{response.status}'"
            raise Exception(msg)

        page_html = BeautifulSoup(await response.text(), "html.parser")

    # get all search results
    results = page_html.find_all("div", {"id": "collview"})
    result_list = []
    for result in results:
        # get relevant elements
        result: BeautifulSoup
        caption_element = result.find("div", {"class": "caption"})
        a_element = caption_element.find("a")

        # extract data
        title = a_element.text.strip()
        url = a_element.get("href")
        year = int(caption_element.find("span", {"class": "y"}).text.strip())
        audio = result.find("div", {"class": "TopLeft"}).find("span", {"class": "capa-audio"}).text.strip()

        # create result object
        result_obj = PobreflixResult(title, year, audio, url)
        result_list.append(result_obj)

    return result_list


async def get_media_pages(imdb: str) -> dict:
    # get media info on imdb
    info = await IMDB.get(imdb, "pt")

    # search for media with matching title and release year
    search_results = await search(info.title)
    pages_list = []
    for result in search_results:
        result: PobreflixResult
        if result.title == info.title and result.year == info.year and result.audio:
            pages_list.append(result)

    if pages_list:
        pages_dict = {}
        for page in pages_list:
            pages_dict.update({page.audio: page.url})

        return pages_dict

    else:
        msg = f"No media found for code '{imdb}'"
        raise Exception(msg)


async def get_sources(url: str):
    async with aiohttp.ClientSession() as session:
        response = await session.get(url)
        html = BeautifulSoup(await response.text(), "html.parser")

    sources = {}
    sources_ul = html.find("ul", {"id": "baixar_menu"})
    for li in sources_ul.find_all("li"):
        li: BeautifulSoup
        a_element = li.find("a")
        url = a_element.get("href")
        text = a_element.find("b").text

        sources.update({text: url})

    return sources


async def movie_streams(imdb: str):
    pages = await get_media_pages(imdb)

    streams = StremioStreamManager()
    if "dub" in pages.keys():
        # get list of links to every avaliable source
        dub_sources = await get_sources(f"{pages['dub']}?area=online")

        # extract stream links from every source
        try:
            streamtape = await stream_from_streamtape(dub_sources["streamtape"])
            streams.add_stream("Pobreflix", "Streamtape (DUB)", streamtape["url"], False, streamtape["headers"])
        except:
            pass

    if "leg" in pages.keys():
        # get list of links to every avaliable source
        leg_sources = await get_sources(f"{pages['leg']}?area=online")

        # extract stream links from every source
        try:
            streamtape = await stream_from_streamtape(leg_sources["streamtape"])
            streams.add_stream("Pobreflix", "Streamtape (LEG)", streamtape["url"], False, streamtape["headers"])
        except:
            pass

    # format as a stremio json
    return streams.to_dict()


async def get_epiosode_url(url: str, season: int, episode: int) -> str | None:
    async with aiohttp.ClientSession() as session:
        # get page of the desired season
        season_url = f"{url}?temporada={season}"
        season_response = await session.get(season_url)

        season_html = BeautifulSoup(await season_response.text(), "html.parser")

    # get url of the desired episode
    a_elements = season_html.find("ul", {"id": "listagem"}).find_all("a")
    episode = str(episode).zfill(2)
    episode_url = None
    for a in a_elements:
        a: BeautifulSoup
        if episode in a.text:
            episode_url = a.get("href")

    return episode_url


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
                streamtape = await stream_from_streamtape(dub_sources["streamtape"])
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
                streamtape = await stream_from_streamtape(leg_sources["streamtape"])
                streams.add_stream("Pobreflix", "Streamtape (LEG)", streamtape["url"], False, streamtape["headers"])
            except:
                pass

    return streams.to_dict()


if __name__ == "__main__":
    print(asyncio.run(series_stream("tt1305826", 8, 9)))
