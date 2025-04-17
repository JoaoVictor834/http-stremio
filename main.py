from urllib.parse import urlparse
import asyncio
import ast

import aiohttp
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException

from scrapers import pobreflix, redecanais

ALLOWED_PROXY_HOSTS = [
    *redecanais.HOSTS,
]

app = FastAPI(debug=True)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MANIFEST = {
    "id": "org.stremio.huuuuuugo.httpstreams",
    "version": "0.0.2",
    "name": "HTTP Stream",
    "description": "Stream videos over http",
    "types": ["movie", "series"],
    "catalogs": [],
    "resources": ["stream"],
    "idPrefixes": ["tt"],
}


# manifest route
@app.get("/manifest.json")
async def addon_manifest():
    return JSONResponse(MANIFEST)


# movie stream route
@app.get("/stream/movie/{id}.json")
async def movie_stream(request: Request):
    id = request.path_params.get("id")

    tasks = [
        pobreflix.movie_streams(id),
        redecanais.movie_streams(id, True),
    ]
    results = await asyncio.gather(*tasks)
    streams = []
    for result in results:
        streams += result

    return JSONResponse({"streams": streams})


# serie stream route
@app.get("/stream/series/{id}:{season}:{episode}.json")
async def series_stream(request: Request):
    id = request.path_params.get("id")
    season = int(request.path_params.get("season"))
    episode = int(request.path_params.get("episode"))

    tasks = [
        pobreflix.series_stream(id, season, episode),
        redecanais.series_stream(id, season, episode, True),
    ]
    results = await asyncio.gather(*tasks)
    streams = []
    for result in results:
        streams += result

    return JSONResponse({"streams": streams})


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


@app.get("/proxy/")
async def read_root(request: Request, url: str, headers: str | None = None):
    # check if the url host is on the allow list
    host = urlparse(url).hostname
    if host not in ALLOWED_PROXY_HOSTS:
        raise HTTPException(403, "Host not allowed")

    # turn request headers into a dict
    request_headers = {key.lower(): request.headers.get(key) for key in request.headers.keys()}

    # create headers dict that will be used on the request to the host
    if headers is not None:
        headers = ast.literal_eval(headers)
    else:
        headers = {}

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

    # return stream
    return StreamingResponse(
        yield_chunks(request, session, response),
        headers=response_headers,
        status_code=response.status,
    )


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=6222,
        ssl_keyfile="localhost.key",
        ssl_certfile="localhost.crt",
    )
