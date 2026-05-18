from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import TelegramObject

from src.common.services.cache import CacheService


class CacheMiddleware(BaseMiddleware):
    def __init__(self, cache: CacheService):
        self.cache = cache

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        need_cache = get_flag(data, "need_cache")

        if not need_cache:
            await handler(event, data)

        data["cache"] = self.cache
        await handler(event, data)
