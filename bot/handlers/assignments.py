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

        # NOTE: your condition was wrong. This is safer:
        if isinstance(data, dict) and int(data.get("status_code") or 200) == 403:
            msg = (
                "🌿 <b>Your data is being prepared.</b>\n\n"
                "Please give us a little time — everything will be ready soon.\n"
                "We will notify you within 24 hours when it’s ready.\n\n"
                "If it takes longer than expected, please contact the admin.\n"
                "Thank you for your patience 🤍"
            )
            await safe_send_html(update.effective_chat, msg, reply_markup=menu_for_user_type(user_type))
            return

    header = texts.assignments_title(
        data.get("first_name"), data.get("last_name"), data.get("student_id")
    )
    subjects = data.get("subjects") or []
    now = datetime.now(tz)

    # -------------------------
    # Collect pending assignments
    # -------------------------
    pending_assignments = []
    for s in subjects:
        code = s.get("subject") or "-"
        assigns = s.get("assignments") or []
        for a in assigns:
            if (a.get("submission") or "").strip() != "No submission":
                continue
            due_str = a.get("due_date") or ""
            due_dt = parse_due_dt(due_str, settings.tz)
            pending_assignments.append((due_dt, code, a))

    pending_assignments.sort(key=lambda x: (x[0] is None, x[0] or datetime.max.replace(tzinfo=tz)))

    # -------------------------
    # Collect quizzes
    # -------------------------
    open_quizzes = []      # not finished / still relevant
    finished_quizzes = []  # submitted / closed

    for s in subjects:
        code = s.get("subject") or "-"
        quizzes = s.get("quizzes") or []
        for q in quizzes:
            closes_str = q.get("quiz_closes") or ""
            closes_dt = parse_due_dt(closes_str, settings.tz)

            status = (q.get("status") or "").strip().lower()
            grade = q.get("grade")

            is_finished = False
            if status in {"submitted", "finished", "closed"}:
                is_finished = True
            elif closes_dt and closes_dt < now:
                # closed by time
                is_finished = True

            item = (closes_dt, code, q)

            if is_finished:
                finished_quizzes.append(item)
            else:
                open_quizzes.append(item)

    open_quizzes.sort(key=lambda x: (x[0] is None, x[0] or datetime.max.replace(tzinfo=tz)))
    finished_quizzes.sort(key=lambda x: (x[0] is None, x[0] or datetime.max.replace(tzinfo=tz)))

    # If nothing to show
    if not pending_assignments and not open_quizzes and not finished_quizzes:
        await safe_send_html(
            update.effective_chat,
            "✅ <b>All clear!</b>\nNo pending assignments or quizzes right now.",
            reply_markup=menu_for_user_type(user_type),
        )
        return

    # -------------------------
    # Build message
    # -------------------------
    lines = [header, ""]

    # Assignments section
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
        lines.append("📝 <b>Pending Assignments</b>\n✅ No pending assignments.")

    lines.append("")

    # Open quizzes section
    if open_quizzes:
        lines.append("🧩 <b>Quizzes (Open / Upcoming)</b>")
        for closes_dt, code, q in open_quizzes:
            name = q.get("name") or "Quiz"
            url = q.get("url") or ""
            closes_str = q.get("quiz_closes") or "-"
            left = format_time_left(now, closes_dt) if closes_dt else ""
            status = q.get("status") or "Open"

            lines.append(f"\n📘 <b>{code}</b> — <b>{name}</b>")
            lines.append(f"📅 Closes: <b>{closes_str}</b>")
            if left:
                lines.append(f"⏰ Left: <b>{left}</b>")
            lines.append(f"📌 Status: <b>{status}</b>")
            if url:
                lines.append(f"🔗 <a href='{url}'>Open</a>")
    else:
        lines.append("🧩 <b>Quizzes (Open / Upcoming)</b>\n✅ No open quizzes.")

    lines.append("")

    # Finished quizzes section (keep short: show only last few)
    if finished_quizzes:
        lines.append("✅ <b>Recently Finished Quizzes</b>")
        for closes_dt, code, q in finished_quizzes[-5:]:
            name = q.get("name") or "Quiz"
            grade = q.get("grade")
            closes_str = q.get("quiz_closes") or "-"
            grade_text = f"{grade}" if grade else "-"
            lines.append(f"\n📘 <b>{code}</b> — <b>{name}</b>")
            lines.append(f"📅 Closed: <b>{closes_str}</b>")
            lines.append(f"🧾 Grade: <b>{grade_text}</b>")

    msg = "\n".join(lines).strip()
    await safe_send_html(update.effective_chat, msg, reply_markup=menu_for_user_type(user_type))
