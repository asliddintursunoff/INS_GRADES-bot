from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from bot.api_client import BackendClient, ApiError
from bot.config import Settings
from bot.keyboards import (
    BTN_TIMETABLE,
    BTN_ECLASS,
    BTN_ATTENDANCE,
    BTN_ASSIGNMENTS,
    menu_for_user_type,
)
from bot import texts
from bot.handlers.timetable import show_timetable
from bot.handlers.attendance import show_attendance
from bot.handlers.assignments import show_assignments
from bot.services.user_service import determine_user_type, safe_send_html





async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_type: str):
    settings: Settings = context.bot_data["settings"]
    telegram_id = str(update.effective_user.id)

    first_name = None
    try:
        async with BackendClient(settings.base_url, settings.http_timeout_seconds) as api:
            info = await api.get_user_info(telegram_id)
            if info:
                first_name = info.get("first_name")
    except Exception:
        first_name = None

    msg = texts.intro(first_name, user_type)
    await safe_send_html(update.effective_chat, msg, reply_markup=menu_for_user_type(user_type))


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Show help + menu again
    settings: Settings = context.bot_data["settings"]
    telegram_id = str(update.effective_user.id)
    user_type = await determine_user_type(settings, telegram_id)
    if context.user_data.get("in_eclass_flow"):
        return

    await safe_send_html(update.effective_chat, texts.help_text(), reply_markup=menu_for_user_type(user_type))


def build_menu_handlers():
    """
    ✅ IMPORTANT:
    - We still register all handlers, but inside each handler you should check user_type if needed.
    - Unknown fallback stays last.
    """
    return [
        MessageHandler(filters.Regex(f"^{BTN_TIMETABLE}$"), show_timetable),
        MessageHandler(filters.Regex(f"^{BTN_ATTENDANCE}$"), show_attendance),
        MessageHandler(filters.Regex(f"^{BTN_ASSIGNMENTS}$"), show_assignments),
    #    # E-class has its own ConversationHandler entry
    #             MessageHandler(
    #         filters.TEXT & ~filters.COMMAND & ~filters.Regex(f"^{BTN_ECLASS}$"),
    #         unknown_message
    #     )

    ]
