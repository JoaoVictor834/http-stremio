from urllib.parse import urlencode, urlparse
import asyncio
import re

import aiohttp
from fastapi import Request
from fastapi.exceptions import HTTPException

from . import constants


def check_allowed_urls(url: str):
    # try url against the list of allowed hosts
    hostname = urlparse(url).hostname
    if hostname in constants.ALLOWED_HOSTS:
        return

    # try url against the list of allowed regular expressions
    for pattern in constants.ALLOWED_REGEXS:
        if re.match(pattern, url):
            return

    # block request if everything else fails
    raise HTTPException(403, f"URL blocked by proxy: The URL '{url}' does not match any of the allowed hosts or regular expressions.")


async def yield_chunks(request: Request, session: aiohttp.ClientSession, response: aiohttp.ClientResponse, chunk_size: int = 8192):
    """Takes a `ClientSession` and `ClientResponse` object and yields chunks for a `StreamingResponse`.

    Also closes both objects after a connection is closed or the files is fully streamed.
    """
    # iterate through the response content yielding chunks
    try:
        async for chunk in response.content.iter_chunked(chunk_size):
            # check if client disconnects
            if await request.is_disconnected():
                break
            yield chunk

    # triggered when client disconnects mid-stream
    except asyncio.CancelledError:
        print("Stream cancelled by client!")
        raise HTTPException(status_code=499)

    # handle host errors
    except Exception as e:
        print(f"Streaming erro: {e}")
        raise HTTPException(status_code=502, detail="Upstream CDN error")

    # cleanup
    finally:
        response.release()
        await session.close()


def add_proxy_to_hls_parts(m3u8_content: str, headers: dict | None = None):
    if headers is None:
        headers = {}

    lines = m3u8_content.split("\n")
    for i, line in enumerate(lines):
        url_matches = re.match(r"https?://[a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,})(:\d+)?(/[^\s]*)?", line)
        if url_matches:
            # update url to use the local proxy
            url = url_matches[0]
            query = urlencode({"url": url, "headers": headers})
            lines[i] = f"?{query}"

    return "\n".join(lines)
