from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker


class DatabaseSessionMiddleware(BaseMiddleware):
    def __init__(self, sessionmaker: async_sessionmaker):  # type: ignore
        self.sessionmaker = sessionmaker

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        need_db_session = get_flag(data, "need_db_session")

        if not need_db_session:
            await handler(event, data)

        async with self.sessionmaker() as session:
            data["db_session"] = session
            try:
                await handler(event, data)
                await session.commit()
            except Exception:
                await session.rollback()
                raise
