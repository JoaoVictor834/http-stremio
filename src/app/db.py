from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from .proxy.models import Base


DATABASE_URL = "sqlite+aiosqlite:///sqlite3.db"

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(engine)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
