import asyncio
import ast

import requests
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from scrapers import pobreflix, redecanais


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

    streams = await pobreflix.series_stream(id, season, episode)

    return JSONResponse({"streams": streams})


@app.get("/proxy/")
async def read_root(request: Request, url: str, headers: str | None = None):
    if headers is not None:
        headers = ast.literal_eval(headers)
    else:
        headers = {}

    range = request.headers.get("Range")
    status = 200
    if range:
        headers.update({"Range": range})
        status = 201

    response = requests.get(url, headers=headers, stream=True)

    return StreamingResponse(
        response.iter_content(1024 * 1024),
        status_code=status,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=6222, ssl_keyfile="localhost.key", ssl_certfile="localhost.crt")
