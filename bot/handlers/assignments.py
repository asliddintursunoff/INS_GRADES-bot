from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.ext import ContextTypes

from bot.config import Settings
from bot.api_client import BackendClient
from bot import texts
from bot.utils import parse_due_dt, format_time_left
from bot.keyboards import menu_for_user_type
from bot.services.user_service import determine_user_type, safe_send_html


async def show_assignments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.bot_data["settings"]
    telegram_id = str(update.effective_user.id)
    tz = ZoneInfo(settings.tz)

    user_type = await determine_user_type(settings, telegram_id)
    if user_type != "full_user":
        await safe_send_html(
            update.effective_chat,
            "⚠️ Assignments are available only after connecting E-class.\nPress 🎓 E-class first.",
            reply_markup=menu_for_user_type(user_type),
        )
        return

    async with BackendClient(settings.base_url, settings.http_timeout_seconds) as api:
        data = await api.get_eclass_info(telegram_id)
  
        if data.get("status_code") or 200 ==  403:
            msg = (
                 "🌿 <b>Your data is currently being prepared.</b>\n\n"
                "Please give us a little time — everything will be ready soon.\n"
                "We will notify you within 24 hours once your data is fully set up.\n\n"
                "If it takes longer than expected, Please contact with admin.\n"
                "Thank you for your patience 🤍"
            )
            await safe_send_html(update.effective_chat, msg, reply_markup=menu_for_user_type(user_type))
            return


    header = texts.assignments_title(data.get("first_name"), data.get("last_name"), data.get("student_id"))
    subjects = data.get("subjects") or []

    pending = []
    for s in subjects:
        code = s.get("subject") or "-"
        assigns = s.get("assignments") or []
        for a in assigns:
            if (a.get("submission") or "").strip() != "No submission":
                continue
            due_str = a.get("due_date") or ""
            due_dt = parse_due_dt(due_str, settings.tz)
            pending.append((due_dt, code, a))

    pending.sort(key=lambda x: (x[0] is None, x[0] or datetime.max.replace(tzinfo=tz)))

    if not pending:
        await safe_send_html(
            update.effective_chat,
            texts.no_pending_assignments(),
            reply_markup=menu_for_user_type(user_type),
        )
        return

    now = datetime.now(tz)

    lines = [header]
    for due_dt, code, a in pending:
        name = a.get("name") or "Assignment"
        url = a.get("url") or ""
        due_str = a.get("due_date") or "-"
        left = ""
        if due_dt:
            left = format_time_left(now, due_dt)

        lines.append(f"📘 <b>{code}</b>")
        lines.append(f"📝 <b>{name}</b>")
        lines.append(f"📅 Due: <b>{due_str}</b>")
        if left:
            lines.append(f"⏰ Time left: <b>{left}</b>")
        if url:
            lines.append(f"🔗 <a href='{url}'>Open</a>")
        lines.append("")

    msg = "\n".join(lines).strip()
    await safe_send_html(update.effective_chat, msg, reply_markup=menu_for_user_type(user_type))
