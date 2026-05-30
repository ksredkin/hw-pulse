from datetime import datetime, timedelta, timezone

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import FSInputFile, Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.core.config import BOT_PHOTO_PATH
from src.bot.keyboard.inline import create_inline_keyboard
from src.bot.messages.messages import start_message
from src.bot.services.user import UserService
from src.common.repositories.user_repository import UserRepository
from src.common.services.cache import CacheService

command_router = Router()


@command_router.message(CommandStart(), flags={"need_cache": True})
async def start(message: Message, cache: CacheService) -> None:
    image_id = await cache.get_image_id_from_cache("start")

    if image_id:
        try:
            await message.answer_photo(image_id, caption=start_message)  # type: ignore
            return
        except Exception:
            pass

    try:
        image = FSInputFile(BOT_PHOTO_PATH)
        sent = await message.answer_photo(image, caption=start_message)
        try:
            if getattr(sent, "photo", None):
                file_id = sent.photo[-1].file_id  # type: ignore
                await cache.set_image_id_in_cache("start", file_id)
        except Exception:
            pass
    except Exception:
        await message.answer(start_message)


@command_router.message(
    Command("connect"), flags={"need_cache": True, "need_db_session": True}
)
async def connect(
    message: Message, cache: CacheService, db_session: AsyncSession
) -> None:
    if not message or not message.from_user:
        return

    repository = UserRepository(db_session)

    existing_user = await repository.get_by_tg_id(message.from_user.id)
    if not existing_user:
        service = UserService(repository)
        new_user = await service.create_user(message.from_user.id)

        if new_user is None:
            await message.answer(
                "<b>🚫 Ошибка:</b> не удалось создать нового пользователя. Попробуйте позже."
            )
            return

        await cache.set_telegram_id_by_api_key(new_user.api_key, new_user.telegram_id)  # type: ignore
        await message.answer(f"<b>🔑 Ваш ключ:</b> <code>{new_user.api_key}</code>")
    else:
        await message.answer(
            f"<b>🔑 Ваш ключ:</b> <code>{existing_user.api_key}</code>"
        )


@command_router.message(Command("stats"), flags={"need_cache": True})
async def stats(message: Message, cache: CacheService) -> None:
    if not message or not message.from_user:
        return

    metrics = await cache.get_metrics(message.from_user.id)

    if not metrics:
        await message.answer(
            "<b>🚫 Ошибка:</b> данных еще нет. Попробуйте еще раз позже."
        )
        return

    text_parts = ["<b>💻 Системные показатели:</b>"]

    if cpu := metrics.get("cpu"):
        freq = cpu.get("frequency", {})
        core_loads = cpu.get("percent_per_core", [])
        loads_str = (
            " ".join(f"{p}%" for p in core_loads) if core_loads else "Нет информации."  # type: ignore
        )
        temp = cpu.get("temperature")
        temp_str = f"{temp}°C" if temp else "Нет информации."

        freq_curr = round(freq.get("current", 0) / 1000, 2)  # type: ignore
        freq_min = round(freq.get("min", 0) / 1000, 2)  # type: ignore
        freq_max = round(freq.get("max", 0) / 1000, 2)  # type: ignore

        text_parts.append(
            f"\n<b>⚡ Процессор:</b>\n"
            f"⚙️ Всего ядер: {cpu.get('cores', 'Н/Д')} (Логических: {cpu.get('cores_logical', 'Н/Д')})\n"
            f"🔥 Нагрузка: {cpu.get('percent', 'Н/Д')}%\n"
            f"📊 По ядрам: {loads_str}\n"
            f"⏱ Частота: {freq_curr} ГГц (Мин: {freq_min} ГГц, Макс: {freq_max} ГГц)\n"
            f"🌡️ Температура: {temp_str}"
        )

    if memory := metrics.get("memory"):
        ram = memory.get("ram", {})
        swap = memory.get("swap", {})

        text_parts.append(
            f"\n<b>🧠 Оперативная память:</b>\n"
            f"💾 Занято: {ram.get('percent', 'Н/Д')}%\n"  # type: ignore
            f"📊 Доступно: {ram.get('available_gb', 'Н/Д')} ГБ из {ram.get('total_gb', 'Н/Д')} ГБ\n"  # type: ignore
            f"🔄 Файл подкачки (Swap): {swap.get('percent', 'Н/Д')}%"  # type: ignore
        )

    if disks := metrics.get("disks"):
        disk_text = "\n\n<b>💽 Диски:</b>\n"
        for mount, info in disks.items():
            disk_text += (
                f"📁 <code>{mount}</code>: {info.get('usage_percent', 'Н/Д')}% "  # type: ignore
                f"({info.get('free_gb', 'Н/Д')} ГБ свободно из {info.get('total_gb', 'Н/Д')} ГБ)\n"  # type: ignore
            )
        text_parts.append(disk_text.strip())

    if network := metrics.get("network"):
        text_parts.append(
            f"\n<b>🌐 Сеть (трафик с момента загрузки):</b>\n"
            f"⬇️ Получено: {network.get('read_mb', 'Н/Д')} МБ\n"
            f"⬆️ Отправлено: {network.get('write_mb', 'Н/Д')} МБ"
        )

    if processes := metrics.get("processes"):
        text_parts.append(
            f"\n<b>⚙️ Процессы:</b>\n🔄 Всего запущено: {processes.get('count', 'Н/Д')}"
        )

    await message.answer("\n".join(text_parts))


@command_router.message(Command("temperature"), flags={"need_cache": True})
async def temperature(message: Message, cache: CacheService) -> None:
    if not message or not message.from_user:
        return

    metrics = await cache.get_metrics(message.from_user.id)

    if not metrics:
        await message.answer(
            "<b>🚫 Ошибка:</b> данных еще нет. Попробуйте еще раз позже."
        )
        return

    cpu = metrics.get("cpu")

    if not cpu:
        await message.answer("<b>🚫 Ошибка:</b> данные о процессоре не найдены.")
        return

    temperature = cpu.get("temperature")

    if temperature is None:
        await message.answer(
            "<b>🚫 Ошибка:</b> данные о температуре процессора не найдены."
        )
        return

    await message.answer(f"🌡️ Температура процессора: {temperature}℃")


@command_router.message(
    Command("settings"), flags={"need_cache": True, "need_db_session": True}
)
async def settings(
    message: Message, cache: CacheService, db_session: AsyncSession
) -> None:
    if not message or not message.from_user:
        return

    user_settings = await cache.get_user_settings(message.from_user.id)

    if not user_settings:
        repository = UserRepository(db_session)
        user = await repository.get_by_tg_id(message.from_user.id)

        if not user:
            await message.answer(
                "<b>🚫 Ошибка:</b> Вы еще не подключили устройство. Используйте команду /connect для подключения."
            )
            return

        user_settings = {
            "alert_enabled": bool(user.alert_enabled),
            "alert_temp": int(user.alert_temp),
        }

        await cache.set_user_settings(message.from_user.id, user_settings)

    if user_settings["alert_enabled"]:
        buttons = {
            "🔔 Уведомления о перегреве включены": "switch_overheat_alert_enabled",
            f"🌡️ Изменить порог уведомления о перегреве ({user_settings['alert_temp']}°C)": "change_overheat_alert_temp",
        }
    else:
        buttons = {
            "🔕 Уведомления о перегреве выключены": "switch_overheat_alert_enabled"
        }

    keyboard = create_inline_keyboard(buttons)
    await message.answer("<b>⚙️ Настройки Hardware Pulse</b>", reply_markup=keyboard)


@command_router.message(Command("shutdown"), flags={"need_cache": True})
async def shutdown(message: Message, cache: CacheService) -> None:
    if not message or not message.from_user:
        return

    commands = await cache.get_commands(message.from_user.id) or []
    await cache.set_commands([*commands, "shutdown"], message.from_user.id)
    await message.answer(
        "🛑 Команда выключения отправлена. ПК будет выключен через 5 секунд."
    )


@command_router.message(Command("restart"), flags={"need_cache": True})
async def restart(message: Message, cache: CacheService) -> None:
    if not message or not message.from_user:
        return

    commands = await cache.get_commands(message.from_user.id) or []
    await cache.set_commands([*commands, "restart"], message.from_user.id)
    await message.answer(
        "🔄 Команда перезагрузки отправлена. Ожидаю отключения демона."
    )


@command_router.message(Command("sleep"), flags={"need_cache": True})
async def sleep(message: Message, cache: CacheService) -> None:
    if not message or not message.from_user:
        return

    commands = await cache.get_commands(message.from_user.id) or []
    await cache.set_commands([*commands, "sleep"], message.from_user.id)
    await message.answer("🌙 ПК переводится в спящий режим.")


@command_router.message(Command("ping"), flags={"need_cache": True})
async def ping(message: Message, cache: CacheService) -> None:
    if not message or not message.from_user:
        return

    last_seen = await cache.get_system_last_seen(message.from_user.id)

    if not last_seen:
        await message.answer("🔴 ПК не в сети.")
        return

    now = datetime.now(timezone.utc)
    time_since_last_sent = now - last_seen

    if time_since_last_sent > timedelta(seconds=30):
        await message.answer(
            f"🟢 ПК онлайн! Последний отклик: {time_since_last_sent.total_seconds()} сек назад."
        )
    else:
        await message.answer(
            f"🔴 ПК не в сети. Последний отклик: {time_since_last_sent.total_seconds():.1f} мин назад."
        )
