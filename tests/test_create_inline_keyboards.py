from src.bot.keyboard.inline import create_inline_keyboard, create_cancell_inline_keyboard
from aiogram.types import InlineKeyboardMarkup

def test_create_inline_keyboards() -> None:
    buttons = {"1": "2", "3": "4"}
    keyboard = create_inline_keyboard(buttons)
    assert isinstance(keyboard, InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 2

    cancell_keyboard = create_cancell_inline_keyboard(buttons)
    assert isinstance(cancell_keyboard, InlineKeyboardMarkup)
    assert len(cancell_keyboard.inline_keyboard) == 3
