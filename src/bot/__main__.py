import asyncio
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, FSInputFile, InputProfilePhotoStatic
from singbox2proxy import SingBoxProxy

from src.bot.handlers.command import command_router
from src.bot.middlewares.cache import CacheMiddleware
from src.common.services.cache import cache
from src.common.utils.logger import Logger

logger = Logger("Bot __main__")

bot_commands = [BotCommand(command="stats", description="📈 Состояние пк")]


async def setup_bot(bot: Bot) -> None:
    logger.info("Начата настройка бота")

    bot_name = os.getenv("BOT_NAME")
    bot_before_start_description = os.getenv("BOT_BEFORE_START_DESCRIPTION")
    bot_profile_description = os.getenv("BOT_PROFILE_DESCRIPTION")
    bot_photo_path = os.getenv("BOT_PHOTO_PATH")

    try:
        await bot.set_my_name(bot_name)
        logger.info("Имя бота обновлено")
    except Exception as e:
        logger.warning(f"Не удалось настроить имя бота: {e}")

    try:
        await bot.set_my_description(bot_before_start_description)
        logger.info("Описание бота до start обновлено")
    except Exception as e:
        logger.warning(f"Не удалось настроить описание до start бота: {e}")

    try:
        await bot.set_my_short_description(bot_profile_description)
        logger.info("Описание бота обновлено")
    except Exception as e:
        logger.warning(f"Не удалось настроить описание бота: {e}")

    try:
        await bot.set_my_commands(bot_commands)
        logger.info("Команды бота обновлены")
    except Exception as e:
        logger.warning(f"Не удалось настроить команды бота: {e}")

    try:
        photo = InputProfilePhotoStatic(photo=FSInputFile(bot_photo_path))  # type: ignore
        await bot.set_my_profile_photo(photo=photo)
        logger.info("Фото бота обновлено")
    except Exception as e:
        logger.warning(f"Не удалось настроить фото бота: {e}")

    logger.info("Настройка бота завершена")


async def main() -> None:
    token = os.getenv("BOT_TOKEN")

    if not token:
        logger.error("BOT_TOKEN is not set in environment variables!")
        sys.exit(1)

    proxy = os.getenv("BOT_PROXY")
    vless_proxy = os.getenv("BOT_VLESS_PROXY")

    if proxy:
        session = AiohttpSession(proxy=proxy)
        logger.info("Запуск бота с proxy")
    elif vless_proxy:
        proxy = SingBoxProxy(vless_proxy)
        proxy.start()
        session = AiohttpSession(proxy=proxy.socks5_proxy_url)
        logger.info("Запуск бота с VLESS proxy")
    else:
        session = AiohttpSession()
        logger.info("Запуск бота без proxy")

    properties = DefaultBotProperties(parse_mode=ParseMode.HTML)

    bot = Bot(token, session, properties)
    await setup_bot(bot)

    dp = Dispatcher()
    cache_middleware = CacheMiddleware(cache)

    dp.message.middleware(cache_middleware)

    dp.include_router(command_router)

    await dp.start_polling(bot)


if __name__ == "__init__":
    asyncio.run(main())
