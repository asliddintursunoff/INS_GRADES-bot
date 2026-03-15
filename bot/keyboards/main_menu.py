from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.texts.messages import BTN_TIMETABLE, BTN_BUY_PREMIUM, BTN_ASSIGNMENTS

def get_main_menu(is_subscribed: bool) -> ReplyKeyboardMarkup:
    buttons = []

    if not is_subscribed:
        buttons.append([KeyboardButton(text=BTN_BUY_PREMIUM)])
        buttons.append([KeyboardButton(text=BTN_TIMETABLE)])
    else:
        buttons.append([KeyboardButton(text=BTN_TIMETABLE)])
        buttons.append([KeyboardButton(text=BTN_ASSIGNMENTS)])

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
