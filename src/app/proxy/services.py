from datetime import datetime
import asyncio
import hashlib
import ast
import os

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import aiofiles
import aiohttp

from .utils import str_to_timedelta, get_file_size
from .models import CacheMeta
from .constants import CACHE_DIR

delete_lock = asyncio.Lock()


class CacheMetaServiceExceptions:
    class CacheNotFoundError(Exception):
        pass

    class CacheAlreadyExistsError(Exception):
        pass

    class SimultaneousUpdateError(Exception):
        pass


# TODO: figure out a way to deal with cached responses with status like 429
# TODO: add some docstrings explaining the logic on each method
class CacheMetaService:
    def __init__(self, db: AsyncSession):
        os.makedirs(CACHE_DIR, exist_ok=True)
        self.db = db

    async def create(self, request_url: str, request_headers: dict | None = None, relative_expires_str: str | None = None) -> CacheMeta:
        # set default values if nothing is specified
        if request_headers is None:
            request_headers = {}
        if relative_expires_str is None:
            relative_expires_str = "24h"

        # get hash of url+headers
        hash = hashlib.md5()
        hash.update(f"{request_url} {request_headers}".encode())
        hash = hash.hexdigest()

        # create a new CacheMeta instance with basic values
        cache_meta = CacheMeta(
            id=hash,
            is_downloaded=None,
            request_url=request_url,
            request_headers=str(request_headers),
            created_at=datetime.now(),
            last_used_at=datetime.now(),
        )

        # create new record on the database
        try:
            self.db.add(cache_meta)
            await self.db.commit()
        except IntegrityError:
            msg = f"A record for '{request_url}' and '{request_headers}' already exists!"
            raise CacheMetaServiceExceptions.CacheAlreadyExistsError(msg)

        try:
            # run the update method to fill the remaining values
            return await self.update(hash, relative_expires_str)
        except Exception as e:
            # delete the uncompleted record if something fails
            await self.delete(hash)

            raise e

    async def update(self, hash: str, relative_expires_str: str | None = None) -> CacheMeta:
        # get CacheMeta instance
        cache_meta = await self.db.get(CacheMeta, hash)
        if cache_meta is None:
            msg = f"Record with hash '{hash}' could not be found."
            raise CacheMetaServiceExceptions.CacheNotFoundError(msg)

        # if is_downloaded is false, that means the file is already being downloaded/updated
        if cache_meta.is_downloaded is False:
            msg = f"{cache_meta} is already being updated!"
            raise CacheMetaServiceExceptions.SimultaneousUpdateError(msg)

        try:
            # mark record as being downloaded
            cache_meta.is_downloaded = False
            await self.db.commit()

            # re-atach the CacheMeta instance into the current transaction
            cache_meta = await self.db.get(CacheMeta, hash)

            # send the request for the request_url on the record with the request_headers
            # also on the record and save the response to the same file
            cache_path = os.path.join(CACHE_DIR, hash)
            request_url = cache_meta.request_url
            request_headers = ast.literal_eval(cache_meta.request_headers)
            async with aiohttp.ClientSession() as session:
                async with session.get(request_url, headers=request_headers) as response:
                    async with aiofiles.open(cache_path, "wb") as file:
                        async for chunk in response.content.iter_chunked(1024 * 1024):
                            await file.write(chunk)

                    # update the record with the new data
                    cache_meta.cache_size = get_file_size(cache_path)  # update cache_size
                    cache_meta.response_headers = str(dict(response.headers))  # update response_headers
                    cache_meta.response_status = response.status  # update response_status
                    if relative_expires_str is not None:  # update relative_expires_str if needed
                        cache_meta.relative_expires_str = relative_expires_str
                    else:
                        relative_expires_str = cache_meta.relative_expires_str
                    cache_meta.expires_at = datetime.now() + str_to_timedelta(relative_expires_str)  # update expire date

            # set is_downloaded to true
            cache_meta.is_downloaded = True

            # commit changes and return the updated object
            await self.db.commit()
            await self.db.refresh(cache_meta)

            return cache_meta

        except Exception as e:
            # reset is_downloaded to null if anything fails
            cache_meta = await self.db.get(CacheMeta, hash)
            cache_meta.is_downloaded = None
            await self.db.commit()

            raise e

    # TODO FIXME: there might be a race condition on the checks if the cache is pending or has expired
    async def read(self, hash: str, relative_expires_str: str | None = None) -> CacheMeta:
        # get target record
        cache_meta = await self.db.get(CacheMeta, hash)
        if cache_meta is None:
            msg = f"Record with hash '{hash}' could not be found."
            raise CacheMetaServiceExceptions.CacheNotFoundError(msg)

        # check if it's pending to be cached
        if cache_meta.is_downloaded is None:
            cache_meta = await self.update(cache_meta.id, relative_expires_str)

        # check if the cached file has expired
        if datetime.now() > cache_meta.expires_at:
            cache_meta = await self.update(cache_meta.id, relative_expires_str)

        # check if it's already being cached
        # and wait for the download to finish
        while cache_meta.is_downloaded is False:
            await self.db.refresh(cache_meta)
            await asyncio.sleep(0.05)

        # update last_used_at
        cache_meta.last_used_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(cache_meta)

        return cache_meta

    async def delete(self, hash: str):
        # delete record from the database
        async with delete_lock:
            cache_meta = await self.db.get(CacheMeta, hash)
            await self.db.delete(cache_meta)
            await self.db.commit()

        # delete cache file
        cache_path = os.path.join(CACHE_DIR, hash)
        if os.path.exists(cache_path):
            os.remove(cache_path)

    async def read_from_url(self, request_url: str, request_headers: dict | None = None, relative_expires_str: str | None = None):
        if request_headers is None:
            request_headers = {}

        # get hash of url+headers
        hash = hashlib.md5()
        hash.update(f"{request_url} {request_headers}".encode())
        hash = hash.hexdigest()

        # run the read method
        return await self.read(hash, relative_expires_str)
