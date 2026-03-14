from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.texts.messages import BTN_TIMETABLE, BTN_BUY_PREMIUM, BTN_ASSIGNMENTS, BTN_BACK

def get_main_menu(is_subscribed: bool) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text=BTN_TIMETABLE)]
    ]

    if is_subscribed:
        buttons.append([KeyboardButton(text=BTN_ASSIGNMENTS)])
    else:
        buttons.append([KeyboardButton(text=BTN_BUY_PREMIUM)])

    buttons.append([KeyboardButton(text=BTN_BACK)]) # Including back as per example

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
