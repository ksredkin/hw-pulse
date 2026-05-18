import json

from redis.asyncio import Redis

from src.common.redis.client import r
from src.common.utils.logger import Logger

logger = Logger("Cache Serice")


class CacheService:
    def __init__(self, redis: Redis):
        self.r = redis

    async def _get(self, prefix: str, key: str) -> str | bool | None:
        full_key = f"{prefix}:{key}"
        data: str | bool | None = await self.r.get(full_key)

        if not data:
            logger.info(f"Кэш не найден: {full_key}")
            return None

        logger.info(f"Кэш найден: {full_key}")
        return data

    async def _set(
        self, prefix: str, key: str, value: str, expire: int | None = None
    ) -> None:
        full_key = f"{prefix}:{key}"
        await self.r.set(full_key, value, ex=expire)
        ttl_str = f" (истечет через {expire}с)" if expire else " (без лимита)"
        logger.info(f"Данные сохранены в кэш: {full_key}{ttl_str}")

    async def set_metrics(
        self,
        metrics: dict[
            str,
            dict[str, float | list[float] | dict[str, float]]
            | dict[str, dict[str, float]]
            | dict[str, float]
            | dict[str, int],
        ],
    ) -> None:
        await self._set("system", "metrics", json.dumps(metrics))

    async def get_metrics(
        self,
        metrics: dict[
            str,
            dict[str, float | list[float] | dict[str, float]]
            | dict[str, dict[str, float]]
            | dict[str, float]
            | dict[str, int],
        ],
    ) -> None:
        await self._get("system", "metrics")

    async def get_commands(self) -> list[str]:
        data = await self._get("system", "commands")
        if data is None or isinstance(data, bool):
            return []
        try:
            commands: list[str] = json.loads(data)
            return commands
        except Exception:
            return []

    async def set_commands(self, commands: list[str]) -> None:
        await self._set("system", "commands", json.dumps(commands))


cache = CacheService(r)
