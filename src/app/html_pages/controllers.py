from fastapi import APIRouter, Request

from .views import index, redirect, movie_info, watch_movie, series_info, watch_series

router = APIRouter(prefix="")


@router.get("/")
async def index_route(request: Request):
    return await index()


@router.get("/redirect")
async def redirect_route(url: str):
    return await redirect(url)


@router.get("/movie/{id}")
async def movie_info_route(request: Request, id: str):
    # mount proxy and cache url with the same url used to acces the server
    scheme = request.url.scheme
    hostname = request.url.hostname
    port = request.url.port
    proxy_url = f"{scheme}://{hostname}{f":{port}" if port else ""}/proxy/stream/"
    cache_url = f"{scheme}://{hostname}{f":{port}" if port else ""}/proxy/cache/"

    # other parameters
    user_agent = request.headers.get("user-agent")

    return await watch_movie(id, proxy_url, cache_url, user_agent)


# async def movie_info_route(request: Request, id: str):
#     return await movie_info(id)


@router.get("/series/{id}")
async def series_info_redirect(request: Request, id: str):
    return await series_info(id, 1)


@router.get("/series/{id}/{season}")
async def series_info_route(request: Request, id: str, season: int):
    return await series_info(id, season)


@router.get("/watch/movie/{id}")
async def watch_movie_route(request: Request, id: str):
    # mount proxy and cache url with the same url used to acces the server
    scheme = request.url.scheme
    hostname = request.url.hostname
    port = request.url.port
    proxy_url = f"{scheme}://{hostname}{f":{port}" if port else ""}/proxy/stream/"
    cache_url = f"{scheme}://{hostname}{f":{port}" if port else ""}/proxy/cache/"

    # other parameters
    user_agent = request.headers.get("user-agent")

    return await watch_movie(id, proxy_url, cache_url, user_agent)


@router.get("/watch/series/{id}/{season}/{episode}")
async def watch_series_route(request: Request, id: str, season: int, episode: int):
    # mount proxy and cache url with the same url used to acces the server
    scheme = request.url.scheme
    hostname = request.url.hostname
    port = request.url.port
    proxy_url = f"{scheme}://{hostname}{f":{port}" if port else ""}/proxy/stream/"
    cache_url = f"{scheme}://{hostname}{f":{port}" if port else ""}/proxy/cache/"

    # other parameters
    user_agent = request.headers.get("user-agent")

    return await watch_series(id, season, episode, proxy_url, cache_url, user_agent)
