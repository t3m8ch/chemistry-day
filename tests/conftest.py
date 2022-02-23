import asyncio

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    AsyncEngine
)

from app.core.models import Base
from app.init.settings import UnitTestsSettings, load_settings


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def config() -> UnitTestsSettings:
    return load_settings(type_=UnitTestsSettings)


@pytest_asyncio.fixture(scope="session")
async def db_engine(config: UnitTestsSettings):
    engine = create_async_engine(config.db.url)

    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine: AsyncEngine):
    async with db_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session = AsyncSession(db_engine)

    try:
        yield session
    finally:
        await session.close()
        async with db_engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
