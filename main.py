import asyncio
import ast

import requests
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
    "version": "0.0.1",
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
        redecanais.movie_streams(id),
    ]
    results = await asyncio.gather(*tasks)
    streams = results[0] + results[1]
    print(streams)

    return JSONResponse({"streams": streams})


# serie stream route
@app.get("/stream/series/{id}:{season}:{episode}.json")
async def series_stream(request: Request):
    id = request.path_params.get("id")
    season = int(request.path_params.get("season"))
    episode = int(request.path_params.get("episode"))

    streams = await pobreflix.series_stream(id, season, episode)

    return JSONResponse({"streams": streams})
