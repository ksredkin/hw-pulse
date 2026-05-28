import json

from src.common.database.connection import get_db_session
from src.common.redis.client import r
from src.common.repositories.user_repository import UserRepository
from src.common.services.cache import cache


class AlertService:
    COOLDOWN_SECONDS = 600
    PUBSUB_CHANNEL = "alerts:overheat"

    @classmethod
    async def check_and_publish(cls, telegram_id: int, current_temp: float) -> None:
        settings = await cache.get_user_settings(telegram_id)

        if not settings:
            async with get_db_session() as session:  # type: ignore
                repository = UserRepository(session)
                user = await repository.get_by_tg_id(telegram_id)

                if not user:
                    return

                settings = {
                    "alert_enabled": bool(user.alert_enabled),
                    "alert_temp": int(user.alert_temp),
                }
                await cache.set_user_settings(telegram_id, settings)

        if not settings["alert_enabled"] or current_temp < settings["alert_temp"]:
            return

        is_locked = await cache.get_alert_lock(telegram_id)
        if is_locked:
            return

        event_payload = {
            "telegram_id": telegram_id,
            "temperature": current_temp,
            "threshold": settings["alert_temp"],
        }
        await r.publish(cls.PUBSUB_CHANNEL, json.dumps(event_payload))
        await cache.set_alert_lock(telegram_id, cls.COOLDOWN_SECONDS)
