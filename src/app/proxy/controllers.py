import ast

from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .views import stream_proxy, cache_proxy
from ..dependencies import get_db

router = APIRouter(prefix="/proxy")


@router.get("/stream/")
async def stream_proxy_route(request: Request, url: str, headers: None | str = None):
    # create headers dict that will be used on the request to the host
    if headers is not None:
        headers = ast.literal_eval(headers)
    else:
        headers = {}

    # turn request headers into a dict
    request_headers = {key.lower(): request.headers.get(key) for key in request.headers.keys()}

    return await stream_proxy(request, url, headers, request_headers)


@router.get("/cache/")
async def cache_proxy_route(request: Request, url: str, headers: str | None = None, expires: str | None = None, db: AsyncSession = Depends(get_db)):
    # create headers dict that will be used on the request to the host
    if headers is not None:
        headers = ast.literal_eval(headers)
    else:
        headers = {}

    return await cache_proxy(url, headers, expires, db)
