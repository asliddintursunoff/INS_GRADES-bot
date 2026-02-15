from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from bot.config import Settings
from bot.api_client import BackendClient
from bot import texts
from bot.keyboards import menu_for_user_type
from bot.services.user_service import determine_user_type, safe_send_html


DAY_ORDER = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_LABEL = {
    "monday": "Monday",
    "tuesday": "Tuesday",
    "wednesday": "Wednesday",
    "thursday": "Thursday",
    "friday": "Friday",
    "saturday": "Saturday",
    "sunday": "Sunday",
}


def _sort_key(x: dict) -> str:
    return str(x.get("start_time") or "")


async def show_timetable(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.bot_data["settings"]
    telegram_id = str(update.effective_user.id)

    async with BackendClient(settings.base_url, settings.http_timeout_seconds) as api:
        data = await api.get_timetable(telegram_id)

    title = texts.timetable_title(data.get("first_name"), data.get("group_name"))
    timetable = data.get("timetable") or {}

    parts = [title]
    for day in DAY_ORDER:
        items = timetable.get(day) or []
        if not items:
            continue

        parts.append(f"📅 <b>{DAY_LABEL.get(day, day.capitalize())}</b>")
        items_sorted = sorted(items, key=_sort_key)
        for it in items_sorted:
            subj = it.get("subject") or "-"
            name = it.get("subject_name") or ""
            st = it.get("start_time") or "??:??"
            en = it.get("end_time") or "??:??"
            room = it.get("room") or "-"
            parts.append(f"🕒 <b>{st}–{en}</b> | 📘 <b>{subj}</b> — {name} | 🏫 <b>{room}</b>")
        parts.append("")

    msg = "\n".join(parts).strip()

    user_type = await determine_user_type(settings, telegram_id)
    await safe_send_html(update.effective_chat, msg, reply_markup=menu_for_user_type(user_type))
