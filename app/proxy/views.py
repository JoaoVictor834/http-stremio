from urllib.parse import urlparse
import hashlib
import ast
import os

import aiohttp
import aiofiles
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse, FileResponse, Response

from .utils import check_host_allowed, add_proxy_to_hls_parts, yield_chunks
from . import constants


async def stream_proxy(request: Request, url: str, headers: dict, request_headers: dict):
    # check if the url host is on the allow list
    check_host_allowed(url)

    # get headers relevant to the host
    if "range" in request_headers.keys():
        headers.update({"range": request_headers["range"]})

    if "accept" in request_headers.keys():
        headers.update({"accept": request_headers["accept"]})

    # start session and request outside of a context managers
    session = aiohttp.ClientSession()
    response = await session.get(url, headers=headers)

    # get response header as a dict
    response_headers = {key.lower(): response.headers.get(key) for key in response.headers.keys()}

    # remove host's CORS restrictions from response headers
    if "access-control-allow-origin" in response_headers.keys():
        response_headers.update({"access-control-allow-origin": "*"})

    # modify hls streams to use local proxy
    if response_headers["content-type"] in constants.HLS_CONTENT_TYPE_HEADERS:
        updated_content = add_proxy_to_hls_parts(await response.text())
        return Response(
            updated_content,
            response.status,
            headers=response_headers,
        )

    else:
        # return stream
        return StreamingResponse(
            yield_chunks(request, session, response),
            headers=response_headers,
            status_code=response.status,
        )


async def cache_proxy(url: str, headers: dict):
    # check if the url host is on the allow list
    check_host_allowed(url)

    # get hash of url plus headers
    url_hash = hashlib.md5()
    url_hash.update(f"{url} {headers}".encode())
    url_hash = url_hash.hexdigest()

    # download the file if it's not cached already
    os.makedirs(constants.CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(constants.CACHE_DIR, url_hash)
    if not os.path.exists(cache_path):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as file_response:
                # cancel if an invalid status code is received
                if not (200 <= file_response.status <= 299):
                    return HTTPException(status_code=file_response.status)

                # download file
                async with aiofiles.open(cache_path, "wb") as cache_file:
                    async for chunk in file_response.content.iter_chunked(1024):
                        await cache_file.write(chunk)

    return FileResponse(cache_path)
