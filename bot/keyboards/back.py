from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.texts.messages import BTN_BACK

def get_back_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=BTN_BACK, callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
