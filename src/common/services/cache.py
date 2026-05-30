import json
from datetime import datetime, timezone

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

    async def _del(self, prefix: str, key: str) -> None:
        full_key = f"{prefix}:{key}"
        await self.r.delete(full_key)

    async def set_metrics(
        self,
        metrics: dict[
            str,
            dict[str, float | list[float] | dict[str, float]]
            | dict[str, dict[str, float]]
            | dict[str, float]
            | dict[str, int],
        ],
        telegram_id: int,
    ) -> None:
        await self._set(f"system:{telegram_id}", "metrics", json.dumps(metrics))

    async def get_metrics(
        self, telegram_id: int
    ) -> dict[
        str,
        dict[str, float | list[float] | dict[str, float]]
        | dict[str, dict[str, float]]
        | dict[str, float]
        | dict[str, int],
    ]:
        try:
            metrics_json = await self._get(f"system:{telegram_id}", "metrics")

            if not isinstance(metrics_json, str):
                return {}

            metrics: dict[
                str,
                dict[str, float | list[float] | dict[str, float]]
                | dict[str, dict[str, float]]
                | dict[str, float]
                | dict[str, int],
            ] = json.loads(metrics_json)
            return metrics
        except Exception:
            return {}

    async def get_commands(self, telegram_id: int) -> list[str]:
        data = await self._get(f"system:{telegram_id}", "commands")
        if data is None or isinstance(data, bool):
            return []
        try:
            commands: list[str] = json.loads(data)
            return commands
        except Exception:
            return []

    async def set_commands(self, commands: list[str], telegram_id: int) -> None:
        await self._set(f"system:{telegram_id}", "commands", json.dumps(commands))

    async def clear_commands(self, telegram_id: int) -> None:
        await self._del(f"system:{telegram_id}", "commands")

    async def get_image_id_from_cache(self, image: str) -> str | bool | None:
        return await self._get("image", image)

    async def set_image_id_in_cache(self, image: str, image_id: str) -> None:
        await self._set("image", image, image_id)

    async def set_telegram_id_by_api_key(self, api_key: str, telegram_id: int) -> None:
        await self._set("auth", api_key, str(telegram_id), 3600)

    async def get_telegram_id_by_api_key(self, api_key: str) -> None | int:
        result = await self._get("auth", api_key)
        return int(result) if isinstance(result, str) else None

    async def set_alert_lock(self, telegram_id: int, ttl: int) -> None:
        await self._set("lock:alert", str(telegram_id), "1", ttl)

    async def get_alert_lock(self, telegram_id: int) -> str | bool | None:
        return await self._get("lock:alert", str(telegram_id))

    async def get_user_settings(self, telegram_id: int) -> dict[str, int | bool] | None:
        result = await self._get("settings", str(telegram_id))
        return json.loads(str(result)) if result else None

    async def set_user_settings(
        self, telegram_id: int, settings: dict[str, int | bool]
    ) -> None:
        await self._set("settings", str(telegram_id), json.dumps(settings), 3600)

    async def update_system_last_seen(self, telegram_id: int) -> None:
        now = datetime.now(timezone.utc)
        await self._set(f"system:{telegram_id}", "last_seen", now.isoformat())

    async def get_system_last_seen(self, telegram_id: int) -> datetime | None:
        result = await self._get(f"system:{telegram_id}", "last_seen")
        return datetime.fromisoformat(result) if isinstance(result, str) else None


cache = CacheService(r)
