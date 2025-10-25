import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

from domain import Base


class DatabaseHelper:

    def __init__(self, db_url: str | None = None):
        database_url = db_url or (
            f"postgresql+asyncpg://"
            f"{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
            f"@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', 5432)}"
            f"/{os.getenv('POSTGRES_DB')}"
        )
        self._engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300
        )
        self.session_maker = async_sessionmaker(
            bind=self._engine,
            autoflush=False,
            expire_on_commit=False,
            autocommit=False
        )

    async def session_dependency(self):
        session = self.session_maker()
        try:
            yield session
        finally:
            await session.close()

    async def create_schema(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def del_schema(self):
        async with self._engine.begin() as conn:
            # Удаляем таблицы с CASCADE для обработки зависимостей
            await conn.execute(text("DROP SCHEMA public CASCADE"))
            await conn.execute(text("CREATE SCHEMA public"))

    async def close(self):
        await self._engine.dispose()
