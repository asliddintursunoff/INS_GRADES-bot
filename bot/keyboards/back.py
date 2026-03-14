from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.texts.messages import BTN_BACK

def get_back_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text=BTN_BACK)]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
