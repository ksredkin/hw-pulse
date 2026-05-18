from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from src.bot.messages.messages import start_message
from src.common.services.cache import CacheService

command_router = Router()


@command_router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(start_message)


@command_router.message(Command("stats"), flags={"need_cache": True})
async def stats(message: Message, cache: CacheService) -> None:
    metrics = await cache.get_metrics() or "Нет информации."
    await message.answer(str(metrics))


@command_router.message(Command("kukareku"), flags={"need_cache": True})
async def kukareku(message: Message, cache: CacheService) -> None:
    commands = await cache.get_commands()
    await cache.set_commands([*commands, "kukareku"])
    await message.answer("🐓 Kukareku")
