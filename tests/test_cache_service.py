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


@pytest.mark.asyncio
async def test_set_and_get_metrics(redis: FakeRedis) -> None:
    cache = CacheService(redis)
    metrics = {
        "cpu": {"usage": 12.5, "history": [1.0, 2.0]},
        "mem": {"total": 1024, "used": 512},
    }

    await cache.set_metrics(metrics)  # type: ignore

    stored = await redis.get("system:metrics")
    assert stored == json.dumps(metrics)

    loaded = await cache.get_metrics()
    assert loaded == metrics


@pytest.mark.asyncio
async def test_get_metrics_returns_empty_if_key_missing(redis: FakeRedis) -> None:
    cache = CacheService(redis)

    loaded = await cache.get_metrics()
    assert loaded == {}


@pytest.mark.asyncio
async def test_set_and_get_image_id(redis: FakeRedis) -> None:
    cache = CacheService(redis)
    image = "ubuntu:latest"
    image_id = "sha256:abc123"

    await cache.set_image_id_in_cache(image, image_id)

    stored = await redis.get("image:ubuntu:latest")
    assert stored == image_id

    loaded = await cache.get_image_id_from_cache(image)
    assert loaded == image_id


@pytest.mark.asyncio
async def test_get_image_id_returns_none_if_missing(redis: FakeRedis) -> None:
    cache = CacheService(redis)

    loaded = await cache.get_image_id_from_cache("nonexistent:image")
    assert loaded is None
