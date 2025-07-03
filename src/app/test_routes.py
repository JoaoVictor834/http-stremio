import ast

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .proxy.models import CacheMeta
from .dependencies import get_db
from .proxy.services import CacheMetaService


router = APIRouter(prefix="/test", tags=["test"])


@router.get("/cache")
async def list_cache(db: AsyncSession = Depends(get_db)):
    stmt = select(CacheMeta)
    results = await db.execute(stmt)
    results = [instance.to_json() for instance in results.scalars().all()]

    return JSONResponse({"count": len(results), "results": results})


@router.get("/cache/{hash}")
async def list_cache(hash: str, db: AsyncSession = Depends(get_db)):
    cache_meta_service = CacheMetaService(db)
    cache_meta = await cache_meta_service.read(hash)

    return JSONResponse(cache_meta.to_json())


@router.post("/cache")
async def create_cache(request_url: str, request_headers: str | None = None, db: AsyncSession = Depends(get_db)):
    if request_headers:
        request_headers = ast.literal_eval(request_headers)
    else:
        request_headers = {}
    cache_meta_service = CacheMetaService(db)
    cache_meta = await cache_meta_service.create(request_url, request_headers)

    return JSONResponse(cache_meta.to_json())


@router.put("/cache")
async def update_cache(hash: str, relative_expires_str: str | None = None, db: AsyncSession = Depends(get_db)):
    cache_meta_service = CacheMetaService(db)
    cache_meta = await cache_meta_service.update(hash, relative_expires_str)

    return JSONResponse(cache_meta.to_json())


@router.delete("/cache")
async def delete_cache(hash: str, db: AsyncSession = Depends(get_db)):
    cache_meta_service = CacheMetaService(db)
    await cache_meta_service.delete(hash)

    return JSONResponse({"message": f"Record with id '{hash}' deleted succesfully."})
