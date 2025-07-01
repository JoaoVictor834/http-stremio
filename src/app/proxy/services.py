from sqlalchemy.ext.asyncio import AsyncSession


class CacheMetaService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self):
        pass

    async def read(self):
        pass

    async def update(self):
        pass

    async def delete(self):
        pass
