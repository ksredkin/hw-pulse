import os

os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"

import json

import pytest
from fakeredis.aioredis import FakeRedis

from src.common.services.cache import CacheService


@pytest.mark.asyncio
async def test_set_and_get_commands(redis: FakeRedis) -> None:
    cache = CacheService(redis)
    commands = ["start", "stop", "status"]

    await cache.set_commands(commands)

    stored = await redis.get("system:commands")
    assert stored == json.dumps(commands)

    loaded = await cache.get_commands()
    assert loaded == commands


@pytest.mark.asyncio
async def test_get_commands_returns_empty_if_key_missing(redis: FakeRedis) -> None:
    cache = CacheService(redis)

    loaded = await cache.get_commands()
    assert loaded == []
