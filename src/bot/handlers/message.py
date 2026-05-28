from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.states.settings_states import UpdateOverheatAlertTemp
from src.common.repositories.user_repository import UserRepository
from src.common.services.cache import CacheService

message_router = Router()


@message_router.message(
    UpdateOverheatAlertTemp.waiting_for_temp,
    F.text,
    flags={"need_cache": True, "need_db_session": True},
)
async def handle_new_alert_temp(
    message: Message, cache: CacheService, db_session: AsyncSession, state: FSMContext
) -> None:
    if not message or not message.from_user or not message.text:
        return

    try:
        new_temp = int(message.text.strip())
    except ValueError:
        await message.answer(
            "<b>🚫 Ошибка:</b> ожидается целое число. Попробуйте еще раз, например: 90"
        )
        return

    if not (20 <= new_temp <= 150):
        await message.answer(
            "<b>🚫 Ошибка:</b> Температура должна быть в диапазоне от 20 до 150 градусов."
        )
        return

    repository = UserRepository(db_session)
    user = await repository.get_by_tg_id(message.from_user.id)

    if not user:
        await message.answer(
            "<b>🚫 Ошибка:</b> Вы еще не подключили устройство. Используйте команду /connect для подключения."
        )
        await state.clear()
        return

    try:
        await repository.update_settings_by_tg_id(
            message.from_user.id, alert_temp=new_temp
        )

        new_user_settings = {
            "alert_enabled": bool(user.alert_enabled),
            "alert_temp": new_temp,
        }

        await cache.set_user_settings(message.from_user.id, new_user_settings)
        await message.answer("✅ Значение обновлено!")
    except Exception:
        await message.answer(
            "<b>🚫 Ошибка:</b> не удалось обновить порог оповещения. Попробуйте позже."
        )
    finally:
        await state.clear()
