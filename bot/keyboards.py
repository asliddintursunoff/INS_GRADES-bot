from __future__ import annotations

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# Buttons (reply keyboard)
BTN_TIMETABLE = "📅 Timetable"
BTN_ECLASS = "🎓 E-class"
BTN_ATTENDANCE = "📊 Attendance"
BTN_ASSIGNMENTS = "📝 Assignments"
BTN_BACK = "🔙 Back"

# Callback data (inline)
CB_CONFIRM_ID = "confirm_student_id"
CB_CHANGE_ID = "change_student_id"
CB_BACK = "back"
CB_START_AGAIN = "start_again"


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()

from telegram import ReplyKeyboardMarkup

BTN_BACK = "⬅️ Back"

def back_only_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[BTN_BACK]], resize_keyboard=True)


def menu_half_user() -> ReplyKeyboardMarkup:
    # ✅ Only timetable + e-class
    return ReplyKeyboardMarkup(
        [[BTN_TIMETABLE], [BTN_ECLASS]],
        resize_keyboard=True,
        is_persistent=True,
    )


def menu_full_user() -> ReplyKeyboardMarkup:
    # ✅ Only timetable + attendance + assignments (NO E-class)
    return ReplyKeyboardMarkup(
        [[BTN_TIMETABLE], [BTN_ATTENDANCE, BTN_ASSIGNMENTS]],
        resize_keyboard=True,
        is_persistent=True,
    )


def menu_new_user() -> ReplyKeyboardMarkup:
    # minimal while registering
    return ReplyKeyboardMarkup([[BTN_BACK]], resize_keyboard=True, is_persistent=True)


def menu_for_user_type(user_type: str) -> ReplyKeyboardMarkup:
    if user_type == "full_user":
        return menu_full_user()
    if user_type == "half_user":
        return menu_half_user()
    return menu_new_user()


def confirm_student_id_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Confirm", callback_data=CB_CONFIRM_ID),
                InlineKeyboardButton("✏️ Change", callback_data=CB_CHANGE_ID),
            ],
            [InlineKeyboardButton("🔙 Back", callback_data=CB_BACK)],
        ]
    )


def start_again_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔄 Start again", callback_data=CB_START_AGAIN)]]
    )
