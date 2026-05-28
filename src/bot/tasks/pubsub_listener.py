import asyncio
import json

from aiogram import Bot

from src.common.redis.client import r
from src.common.utils.logger import Logger

logger = Logger(__name__)


async def listen_for_alerts(bot: Bot) -> None:
    pubsub = r.pubsub()
    await pubsub.subscribe("alerts:overheat")
    logger.info("Started listening for overheat alerts...")

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])

                text = (
                    f"⚠️ <b>ВНИМАНИЕ: ПЕРЕГРЕВ!</b>\n\n"
                    f"🌡 Текущая температура: <b>{data['temperature']}°C</b>\n"
                    f"⚙️ Ваш лимит: {data['threshold']}°C"
                )

                try:
                    await bot.send_message(chat_id=data["telegram_id"], text=text)
                except Exception as e:
                    logger.error(f"Failed to send alert to {data['telegram_id']}: {e}")
    except asyncio.CancelledError:
        logger.info("PubSub listener stopped.")
