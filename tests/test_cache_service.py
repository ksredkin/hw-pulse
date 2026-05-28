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

    test_telegram_id = 12345

    await cache.set_commands(commands, test_telegram_id)

    stored = await redis.get(f"system:{test_telegram_id}:commands")
    assert stored == json.dumps(commands)

    loaded = await cache.get_commands(test_telegram_id)
    assert loaded == commands


@pytest.mark.asyncio
async def test_get_commands_returns_empty_if_key_missing(redis: FakeRedis) -> None:
    cache = CacheService(redis)

    test_telegram_id = 12345

    loaded = await cache.get_commands(test_telegram_id)
    assert loaded == []


@pytest.mark.asyncio
async def test_set_and_get_metrics(redis: FakeRedis) -> None:
    cache = CacheService(redis)
    metrics = {
        "cpu": {"usage": 12.5, "history": [1.0, 2.0]},
        "mem": {"total": 1024, "used": 512},
    }

    test_telegram_id = 12345

    await cache.set_metrics(metrics, test_telegram_id)  # type: ignore

    stored = await redis.get(f"system:{test_telegram_id}:metrics")
    assert stored == json.dumps(metrics)

    loaded = await cache.get_metrics(test_telegram_id)
    assert loaded == metrics


@pytest.mark.asyncio
async def test_get_metrics_returns_empty_if_key_missing(redis: FakeRedis) -> None:
    cache = CacheService(redis)

    test_telegram_id = 12345

    loaded = await cache.get_metrics(test_telegram_id)
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


@pytest.mark.asyncio
async def test_set_and_get_telegram_id_by_api_key(redis: FakeRedis) -> None:
    cache = CacheService(redis)

    telegram_id = 12345
    api_key = "ABCDE-22-05-2026"

    none_result = await cache.get_telegram_id_by_api_key(api_key)
    assert none_result is None

    await cache.set_telegram_id_by_api_key(api_key, telegram_id)
    normal_result = await cache.get_telegram_id_by_api_key(api_key)
    assert normal_result == telegram_id


@pytest.mark.asyncio
async def test_get_and_set_alert_lock(redis: FakeRedis) -> None:
    cache = CacheService(redis)

    telegram_id = 12345
    ttl = 600

    none_result = await cache.get_alert_lock(telegram_id)
    assert none_result is None

    await cache.set_alert_lock(telegram_id, ttl)

    result = await cache.get_alert_lock(telegram_id)
    assert result == "1"


@pytest.mark.asyncio
async def test_get_and_set_user_settings(redis: FakeRedis) -> None:
    cache = CacheService(redis)

    telegram_id = 12345
    settings = {"alert_enabled": True, "alert_temp": 80}

    none_result = await cache.get_user_settings(telegram_id)
    assert none_result is None

    await cache.set_user_settings(telegram_id, settings)

    result = await cache.get_user_settings(telegram_id)
    assert result == settings
