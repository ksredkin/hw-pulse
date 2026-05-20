from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import FSInputFile, Message

from src.bot.core.config import BOT_PHOTO_PATH
from src.bot.messages.messages import start_message
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


@command_router.message(Command("stats"), flags={"need_cache": True})
async def stats(message: Message, cache: CacheService) -> None:
    metrics = await cache.get_metrics()

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
    metrics = await cache.get_metrics()

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


# commands = await cache.get_commands()
# await cache.set_commands([*commands, "kukareku"])
# await message.answer("🐓 Kukareku")
