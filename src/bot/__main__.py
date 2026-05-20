import asyncio
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, FSInputFile, InputProfilePhotoStatic
from singbox2proxy import SingBoxProxy

from src.bot.core.config import (
    BOT_BEFORE_START_DESCRIPTION,
    BOT_NAME,
    BOT_PHOTO_PATH,
    BOT_PROFILE_DESCRIPTION,
)
from src.bot.handlers.command import command_router
from src.bot.middlewares.cache import CacheMiddleware
from src.common.services.cache import cache
from src.common.utils.logger import Logger

logger = Logger("Bot __main__")

bot_commands = [
    BotCommand(command="start", description="👋 Стартовое сообщение"),
    BotCommand(command="stats", description="💻 Текущие показатели системы"),
    BotCommand(command="temperature", description="🌡️ Текущая температура процессора"),
    ]


async def setup_bot(bot: Bot) -> None:
    logger.info("Начата настройка бота")

    try:
        await bot.set_my_name(BOT_NAME)
        logger.info("Имя бота обновлено")
    except Exception as e:
        logger.warning(f"Не удалось настроить имя бота: {e}")

    try:
        await bot.set_my_description(BOT_BEFORE_START_DESCRIPTION)
        logger.info("Описание бота до start обновлено")
    except Exception as e:
        logger.warning(f"Не удалось настроить описание до start бота: {e}")

    try:
        await bot.set_my_short_description(BOT_PROFILE_DESCRIPTION)
        logger.info("Описание бота обновлено")
    except Exception as e:
        logger.warning(f"Не удалось настроить описание бота: {e}")

    try:
        await bot.set_my_commands(bot_commands)
        logger.info("Команды бота обновлены")
    except Exception as e:
        logger.warning(f"Не удалось настроить команды бота: {e}")

    try:
        photo = InputProfilePhotoStatic(photo=FSInputFile(BOT_PHOTO_PATH))
        await bot.set_my_profile_photo(photo=photo)
        logger.info("Фото бота обновлено")
    except Exception as e:
        logger.warning(f"Не удалось настроить фото бота: {e}")

    logger.info("Настройка бота завершена")


async def main() -> None:
    try:
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
    except Exception as e:
        logger.critical(f"Error occured: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
