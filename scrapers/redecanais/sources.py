# functions to extract stream links from site sources

from urllib.parse import urlencode, parse_qsl, urlparse, urljoin
import re

from bs4 import BeautifulSoup
import aiohttp

from .utils import convert_to_punycode
from .decoders import decode_from_response
from .exceptions import *

REDECANAIS_URL = "https://redecanais.ec"
VIDEO_HOST_URL = "https://xn----------------g34l3fkp7msh1cj3acobj33ac2a7a8lufomma7cf2b1sh.xn---1l1--5o4dxb.xn---22--11--33--99--75---------b25zjf3lta6mwf6a47dza94e.xn--pck.xn--zck.xn--0ck.xn--pck.xn--yck.xn-----0b4asja8cbew2b4b0gd0edbjm2jpa1b1e9zva7a0347s4da2797e7qri.xn--1ck2e1b/player3"


class StreamInfo:
    def __init__(self, url: str, headers: dict | None = None):
        self.url = url
        if headers is None:
            headers = {}
        self.headers = headers


class DownloadStream:
    @classmethod
    async def get_video_player_url(cls, video_page_url: str) -> str:
        """Extract video player url from a given video page, such as the page for a movie or a specific episode of a series"""
        # get video page
        async with aiohttp.ClientSession() as session:
            async with session.get(video_page_url) as video_page_response:
                decoded_video_page = await decode_from_response(video_page_response)
                video_page_html = BeautifulSoup(decoded_video_page, "html.parser")

            # get video url
            video_url = ""
            for iframe in video_page_html.find_all("iframe"):
                name = iframe.get("name")
                if name is not None and name == "Player":
                    video_url = iframe.get("src")
                    video_url = f"{REDECANAIS_URL}{video_url}"

            if video_url:
                return video_url
            else:
                msg = "Failed to extract video url from video page"
                raise VideoPageParsningError(msg)

    @classmethod
    async def get_download_page_url(cls, video_player_url: str) -> str:
        """Get the url of the download page of the given video player url"""
        async with aiohttp.ClientSession() as session:
            async with session.get(video_player_url, allow_redirects=False) as redirect:
                # idna encode url to work with requests
                encoded_url = redirect.headers["location"]
                try:
                    idna_url = convert_to_punycode(f"https:{encoded_url}")
                except:
                    idna_url = encoded_url

            # parse the decoded html to extract serverforms url and token from the decoded html
            async with session.get(idna_url) as response:
                decoded_html = BeautifulSoup(await decode_from_response(response), "html.parser")

            scripts = decoded_html.find_all("script")
            for script in scripts:
                url_match = re.findall(r"url: \'\.(/.+?)\'", script.text)
                if url_match:
                    url_match = url_match[0]
                    serverforms_url = f"{VIDEO_HOST_URL}{url_match}"
                    rctoken = re.findall(r"\'rctoken\':\'(.+?)\'", script.text)[0]

            # request the serverforms url
            async with session.post(serverforms_url, data={"rctoken": rctoken}) as serverforms_response:
                # extract download page url from serverforms
                download_page_url = re.findall(r"baixar=\"https://.+?r=(.+?)\"", await serverforms_response.text())

            # return download page url
            if download_page_url:
                return download_page_url[0]
            else:
                msg = "Could not extract download page url from serverforms html"
                raise ServerFormsParsingError(msg)

    @classmethod
    async def get_download_stream_url(cls, download_page_url: str) -> str:
        """Extract the download link from the given download page"""
        # decode download page
        async with aiohttp.ClientSession() as session:
            async with session.get(download_page_url) as download_page_response:
                download_page = await decode_from_response(download_page_response)

            # extract download link from download page
            download_link = re.findall(r"const *redirectUrl *= *\'(.+?)\'", download_page)
            if download_link:
                return f"https:{download_link[0]}"
            else:
                msg = "Could not extract download link from download page"
                raise DownloadPageParsingError(msg)

    @classmethod
    async def get(cls, video_page_url: str) -> StreamInfo:
        video_player_url = await cls.get_video_player_url(video_page_url)
        download_page_url = await cls.get_download_page_url(video_player_url)
        stream = await cls.get_download_stream_url(download_page_url)

        headers = {
            "Referer": download_page_url,
        }

        return StreamInfo(stream, headers=headers)


class PlayerStream:
    @classmethod
    async def get_video_player_url(cls, video_page_url: str) -> str:
        """Extract video player url from a given video page, such as the page for a movie or a specific episode of a series"""
        print("get_video_player_url")
        return await DownloadStream.get_video_player_url(video_page_url)

    @classmethod
    async def format_video_url(cls, video_player_url: str) -> str:
        """Format the original video player url into the url used as a referer to the actual video stream"""
        print("format_video_url")
        # extract query params from the original video player url
        async with aiohttp.ClientSession() as session:
            query_str = video_player_url.split("?", 1)[1]
            query = {pair[0]: pair[1] for pair in parse_qsl(query_str)}

            async with session.get(video_player_url, allow_redirects=False) as redirect:
                # idna encode url to work with requests
                encoded_url = redirect.headers["location"]
                try:
                    idna_url = convert_to_punycode(f"https:{encoded_url}")
                except:
                    idna_url = encoded_url

            # create link to the formated video player url
            new_host = f"https://{urlparse(idna_url).hostname}/"
            new_vid_url = f"{urljoin(new_host, 'player3/server.php')}?{urlencode(query)}"

            return new_vid_url

    @classmethod
    async def get_stream_from_video_url(cls, formated_video_url: str) -> str:
        """Get the video stream url from the formated video player url"""
        print("get_stream_from_video_url")
        # parse the decoded html to extract serverforms url and token from the decoded html
        async with aiohttp.ClientSession() as session:
            async with session.get(formated_video_url) as response:
                decoded_html = BeautifulSoup(await decode_from_response(response), "html.parser")

            scripts = decoded_html.find_all("script")
            for script in scripts:
                url_match = re.findall(r"url: \'\.(/.+?)\'", script.text)
                if url_match:
                    url_match = url_match[0]
                    serverforms_url = f"{VIDEO_HOST_URL}{url_match}"
                    rctoken = re.findall(r"\'rctoken\':\'(.+?)\'", script.text)[0]

            # request the serverforms url
            async with session.post(serverforms_url, data={"rctoken": rctoken}) as serverforms_response:
                # get video stream url from serverforms
                stream = re.findall(r"VID_URL *= *\"(/.+?)\"", await serverforms_response.text())

            # return stream url
            if stream:
                new_host = f"https://{urlparse(formated_video_url).hostname}/"
                stream = urljoin(new_host, stream[0])
                return stream
            else:
                msg = "Could not extract stream url from serverforms html."
                raise ServerFormsParsingError(msg)

    @classmethod
    async def get(cls, video_page_url: str):
        print("get")
        video_player_url = await cls.get_video_player_url(video_page_url)
        fromated_video_url = await cls.format_video_url(video_player_url)
        stream = await cls.get_stream_from_video_url(fromated_video_url)

        headers = {"Referer": fromated_video_url}

        return StreamInfo(stream, headers=headers)


async def download_stream(video_page_url: str) -> StreamInfo:
    return await DownloadStream.get(video_page_url)


async def player_stream(video_page_url: str) -> StreamInfo:
    return await PlayerStream.get(video_page_url)
