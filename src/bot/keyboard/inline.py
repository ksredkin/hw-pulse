from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_inline_keyboard(
    buttons: dict[str, str], adjust: list[int] = [1], repeat: bool = True
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for text, callback in buttons.items():
        builder.button(text=text, callback_data=callback)
    builder.adjust(*adjust, repeat=repeat)
    return builder.as_markup()


def create_cancell_inline_keyboard(
    buttons: dict[str, str] = {},
    adjust: list[int] = [1],
    repeat: bool = True,
) -> InlineKeyboardMarkup:
    new_buttons = buttons.copy()
    new_buttons["🚫 Отмена"] = "cancell"
    return create_inline_keyboard(new_buttons, adjust, repeat)
