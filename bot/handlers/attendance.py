from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from bot.config import Settings
from bot.api_client import BackendClient
from bot import texts
from bot.keyboards import menu_for_user_type
from bot.services.user_service import determine_user_type, safe_send_html


async def show_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings: Settings = context.bot_data["settings"]
    telegram_id = str(update.effective_user.id)

    user_type = await determine_user_type(settings, telegram_id)
    if user_type != "full_user":
        await safe_send_html(
            update.effective_chat,
            "⚠️ Attendance is available only after connecting E-class.\nPress 🎓 E-class first.",
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


        header = texts.attendance_title(
            data.get("first_name"),
            data.get("last_name"),
            data.get("student_id")
        )

        subjects = data.get("subjects") or []

        if not subjects:
            await safe_send_html(
                update.effective_chat,
                "No attendance data found.",
                reply_markup=menu_for_user_type(user_type),
            )
            return

        # Sort: worst subjects first (absence > late > good)
        def sort_key(s):
            att = s.get("attendance") or {}
            return (-int(att.get("absence", 0)), -int(att.get("late", 0)))

        subjects_sorted = sorted(subjects, key=sort_key)

        lines = [header, ""]

        total_abs = 0
        total_late = 0
        total_att = 0

        for s in subjects_sorted:
            code = s.get("subject") or "-"
            name = s.get("subject_name") or ""
            att = s.get("attendance") or {}

            attended = int(att.get("attendance", 0))
            absence = int(att.get("absence", 0))
            late = int(att.get("late", 0))

            total_att += attended
            total_abs += absence
            total_late += late

            # Status indicator
            if absence > 0:
                status = "🔴"
            elif late > 0:
                status = "🟠"
            else:
                status = "🟢"

            lines.append(f"{status} <b>{code}</b> — {name}")
            lines.append(
                f"   ✅ {attended}   ❌ {absence}   ⏳ {late}"
            )
            lines.append("")

        # Summary at bottom
        
        msg = "\n".join(lines).strip()

        await safe_send_html(
            update.effective_chat,
            msg,
            reply_markup=menu_for_user_type(user_type),
        )
