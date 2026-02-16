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

from datetime import datetime
from zoneinfo import ZoneInfo

# uses your existing: parse_due_dt, format_time_left, safe_send_html,
# determine_user_type, menu_for_user_type, BackendClient, Settings, texts


async def show_assignments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.bot_data["settings"]
    telegram_id = str(update.effective_user.id)
    tz = ZoneInfo(settings.tz)

    user_type = await determine_user_type(settings, telegram_id)
    if user_type != "full_user":
        await safe_send_html(
            update.effective_chat,
            "⚠️ This section works after connecting E-class.\nPress 🎓 <b>E-class</b> first.",
            reply_markup=menu_for_user_type(user_type),
        )
        return

    async with BackendClient(settings.base_url, settings.http_timeout_seconds) as api:
        data = await api.get_eclass_info(telegram_id)

        if isinstance(data, dict) and int(data.get("status_code") or 200) == 403:
            msg = (
                "🌿 <b>Your data is being prepared.</b>\n\n"
                "Please wait a little — we will notify you once it’s ready 🤍"
            )
            await safe_send_html(update.effective_chat, msg, reply_markup=menu_for_user_type(user_type))
            return

    header = texts.assignments_title(
        data.get("first_name"), data.get("last_name"), data.get("student_id")
    )

    subjects = data.get("subjects") or []
    now = datetime.now(tz)

    pending_assignments = []
    open_quizzes = []

    for s in subjects:
        code = s.get("subject") or "-"

        # ------------------
        # Assignments
        # ------------------
        assigns = s.get("assignments") or []
        for a in assigns:
            if (a.get("submission") or "").strip() != "No submission":
                continue

            due_str = a.get("due_date") or ""
            due_dt = parse_due_dt(due_str, settings.tz)
            pending_assignments.append((due_dt, code, a))

        # ------------------
        # Quizzes
        # ------------------
        quizzes = s.get("quizzes") or []
        for q in quizzes:
            closes_str = q.get("quiz_closes") or ""
            closes_dt = parse_due_dt(closes_str, settings.tz)
            status = (q.get("status") or "").strip().lower()

            # show only not finished quizzes
            if status in {"submitted", "finished", "closed"}:
                continue

            open_quizzes.append((closes_dt, code, q))

    pending_assignments.sort(key=lambda x: (x[0] is None, x[0] or datetime.max.replace(tzinfo=tz)))
    open_quizzes.sort(key=lambda x: (x[0] is None, x[0] or datetime.max.replace(tzinfo=tz)))

    if not pending_assignments and not open_quizzes:
        await safe_send_html(
            update.effective_chat,
            "✅ <b>All clear!</b>\nNo pending assignments or quizzes.",
            reply_markup=menu_for_user_type(user_type),
        )
        return

    lines = [header, ""]

    # ------------------
    # Assignments Section
    # ------------------
    if pending_assignments:
        lines.append("📝 <b>Pending Assignments</b>")
        for due_dt, code, a in pending_assignments:
            name = a.get("name") or "Assignment"
            url = a.get("url") or ""
            due_str = a.get("due_date") or "-"
            left = format_time_left(now, due_dt) if due_dt else ""

            lines.append(f"\n📘 <b>{code}</b> — <b>{name}</b>")
            lines.append(f"📅 Due: <b>{due_str}</b>")
            if left:
                lines.append(f"⏰ Left: <b>{left}</b>")
            if url:
                lines.append(f"🔗 <a href='{url}'>Open</a>")
    else:
        lines.append("📝 <b>Pending Assignments</b>\n✅ None.")

    lines.append("")

    # ------------------
    # Quizzes Section
    # ------------------
    if open_quizzes:
        lines.append("🧩 <b>Open Quizzes</b>")
        for closes_dt, code, q in open_quizzes:
            name = q.get("name") or "Quiz"
            url = q.get("url") or ""
            closes_str = q.get("quiz_closes") or "-"
            left = format_time_left(now, closes_dt) if closes_dt else ""

            lines.append(f"\n📘 <b>{code}</b> — <b>{name}</b>")
            lines.append(f"📅 Closes: <b>{closes_str}</b>")
            if left:
                lines.append(f"⏰ Left: <b>{left}</b>")
            if url:
                lines.append(f"🔗 <a href='{url}'>Open</a>")
    else:
        lines.append("🧩 <b>Open Quizzes</b>\n✅ None.")

    msg = "\n".join(lines).strip()
    await safe_send_html(update.effective_chat, msg, reply_markup=menu_for_user_type(user_type))
