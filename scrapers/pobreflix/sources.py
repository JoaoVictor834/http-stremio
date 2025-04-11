# functions to extract stream links from site sources

import typing
import re

import aiohttp
from bs4 import BeautifulSoup


class StreamInfo(typing.TypedDict):
    url: str
    headers: dict


async def streamtape(url: str) -> StreamInfo:
    async with aiohttp.ClientSession() as session:
        # get video page
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
            "Referer": "https://pobreflixtv.love/",
        }
        response = await session.get(url, headers=headers)

        # redirect if necessary
        if "window.location.href" in await response.text():
            matches = re.findall(r"window.location.href *= *\"(.+)\" *;?", await response.text())
            redirect_url = matches[0]
            response = await session.get(redirect_url)

        # check status code
        if response.status != 200:
            msg = f"Unexpected status code when getting streamtape url. Expected '200', got '{response.status}'"
            raise Exception(msg)

        html = BeautifulSoup(await response.text(), "html.parser")

    # find script element containing the stream link
    stream_url = ""
    for script in html.find_all("script"):
        matches = re.findall(r"document.getElementById\('ideoooolink'\).innerHTML *?= *?\"/*(.+?)\".*?\('(.+?)'\).(.+?);", script.text)
        if matches:
            # get start and end of the stream url
            start = matches[0][0]
            end = matches[0][1]

            # get offset of the end string
            offset_str = matches[0][2]
            offset = 0
            for char in offset_str:
                char: str
                if char.isdigit():
                    offset += int(char) + 1

            stream_url = "https://" + start + end[offset - 1 :]

    if stream_url:
        return {"url": stream_url, "headers": {}}
    else:
        msg = "Error extracting stream url from streamtape"
        raise Exception(msg)
