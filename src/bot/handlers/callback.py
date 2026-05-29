from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.keyboard.inline import (
    create_cancell_inline_keyboard,
    create_inline_keyboard,
)
from src.bot.states.settings_states import UpdateOverheatAlertTemp
from src.common.repositories.user_repository import UserRepository
from src.common.services.cache import CacheService

callback_router = Router()


@callback_router.callback_query(
    F.data == "switch_overheat_alert_enabled",
    flags={"need_cache": True, "need_db_session": True},
)
async def switch_overheat_alert_enabled(
    callback: CallbackQuery, cache: CacheService, db_session: AsyncSession
) -> None:
    if (
        not callback
        or not callback.from_user
        or not callback.message
        or not hasattr(callback.message, "edit_text")
    ):
        return

    current_settings = await cache.get_user_settings(callback.from_user.id)
    repository = UserRepository(db_session)

    if current_settings:
        current_alert_enabled = current_settings["alert_enabled"]
    else:
        user = await repository.get_by_tg_id(callback.from_user.id)

        if user is None:
            await callback.message.edit_text(
                "<b>🚫 Ошибка:</b> Вы еще не подключили устройство. Используйте команду /connect для подключения."
            )
            return

        current_alert_enabled = user.alert_enabled  # type: ignore

    new_alert_enabled = not current_alert_enabled
    await repository.update_settings_by_tg_id(
        callback.from_user.id, alert_enabled=new_alert_enabled
    )

    if new_alert_enabled:
        buttons = {
            "🔔 Уведомления о перегреве включены": "switch_overheat_alert_enabled",
            f"🌡️ Изменить порог уведомления о перегреве ({current_settings['alert_temp'] if current_settings else user.alert_temp}°C)": "change_overheat_alert_temp",  # type: ignore
        }
    else:
        buttons = {
            "🔕 Уведомления о перегреве выключены": "switch_overheat_alert_enabled"
        }

    keyboard = create_inline_keyboard(buttons)
    await callback.message.edit_text(
        "<b>⚙️ Настройки Hardware Pulse</b>", reply_markup=keyboard
    )


@callback_router.callback_query(F.data == "cancell")
async def cancell(callback: CallbackQuery) -> None:
    if not callback.message or not hasattr(callback.message, "edit_text"):
        return

    await callback.message.edit_text("✅ Действие отменено!")


@callback_router.callback_query(F.data == "change_overheat_alert_temp")
async def change_overheat_alert_temp(
    callback: CallbackQuery, state: FSMContext
) -> None:
    if (
        not callback
        or not callback.from_user
        or not callback.message
        or not hasattr(callback.message, "edit_text")
    ):
        return

    await state.set_state(UpdateOverheatAlertTemp.waiting_for_temp)
    keyboard = create_cancell_inline_keyboard()
    await callback.message.edit_text(
        "📝 Введите новый порог температуры (в ℃):", reply_markup=keyboard
    )
