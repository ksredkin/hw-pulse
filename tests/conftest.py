import fakeredis.aioredis
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.common.database.models import Base


@pytest.fixture
def redis() -> fakeredis.aioredis.FakeRedis:
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


@pytest.fixture
async def sessionmaker() -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    return sessionmaker


@pytest.fixture
def valid_metrics_payload() -> dict[
    str, float | list[float] | dict[str, float | dict[str, float]] | int
]:
    return {
        "cpu": {"temperature": 85.0, "load": 50.0},
        "memory": {"ram": {"used": 4.0, "total": 8.0}},
        "disks": {"C:": {"used": 50.0, "total": 100.0}},
        "network": {"bytes_sent": 100, "bytes_recv": 200},
        "processes": {"count": 150},
    }
