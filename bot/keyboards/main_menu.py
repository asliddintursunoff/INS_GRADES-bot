from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.texts.messages import BTN_TIMETABLE, BTN_BUY_PREMIUM, BTN_ASSIGNMENTS

def get_main_menu(is_subscribed: bool) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=BTN_TIMETABLE, callback_data="timetable")]
    ]

    if is_subscribed:
        buttons.append([InlineKeyboardButton(text=BTN_ASSIGNMENTS, callback_data="assignments")])
    else:
        buttons.append([InlineKeyboardButton(text=BTN_BUY_PREMIUM, callback_data="buy_premium")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
