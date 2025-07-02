import ast

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from . import html_pages, proxy, stremio
from .db import init_db
from .dependencies import get_db
from .proxy.services import CacheMetaService
from .proxy.models import CacheMeta


async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan, debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(html_pages.router)
app.include_router(proxy.router)
app.include_router(stremio.router)


@app.get("/test/cache")
async def list_cache(db: AsyncSession = Depends(get_db)):
    stmt = select(CacheMeta)
    results = await db.execute(stmt)
    results = [instance.to_json() for instance in results.scalars().all()]

    return JSONResponse(results)


@app.post("/test/cache")
async def create_cache(request_url: str, request_headers: str | None = None, db: AsyncSession = Depends(get_db)):
    if request_headers:
        request_headers = ast.literal_eval(request_headers)
    else:
        request_headers = {}
    cache_meta_service = CacheMetaService(db)
    cache_meta = await cache_meta_service.create(request_url, request_headers)

    return JSONResponse(cache_meta.to_json())


@app.put("/test/cache")
async def update_cache(hash: str, relative_expires_str: str | None = None, db: AsyncSession = Depends(get_db)):
    cache_meta_service = CacheMetaService(db)
    cache_meta = await cache_meta_service.update(hash, relative_expires_str)

    return JSONResponse(cache_meta.to_json())


@app.delete("/test/cache")
async def delete_cache(hash: str, db: AsyncSession = Depends(get_db)):
    cache_meta_service = CacheMetaService(db)
    await cache_meta_service.delete(hash)

    return JSONResponse({"message": f"Record with id '{hash}' deleted succesfully."})
