from __future__ import annotations

from typing import Optional
def intro(first_name: str | None, user_type: str) -> str:
    name = first_name or "there"

    return (
        f"👋 Hi <b>{name}</b>!\n\n"
        "🎓 <b>Never miss anything again.</b>\n\n"
        "🔔 Assignment deadline reminders (5, 3, 1 day + due day)\n"
        "🧾 Instant grade notifications\n"
        "📊 Absence & late alerts immediately\n\n"
        "📅 Timetable & class reminders included.\n\n"
        "📌 Pin this chat so you never miss updates."
    )


def ask_student_id() -> str:
    return (
        "🆕 Please enter your <b>Student ID</b>.\n\n"
        "Format must be: <b>U1234567</b> (or <b>u1234567</b>)."
    )


def invalid_student_id() -> str:
    return "❌ Invalid format.\n\nFormat should be <b>U1234567</b> or <b>u1234567</b>."


def confirm_student_id(student_id: str) -> str:
    return (
        f"✅ You entered: <b>{student_id}</b>\n\n"
        "Is it correct?"
    )


def registered_half_user() -> str:
    return (
        "✅ Registered!\n\n"
        "To enable <b>Attendance</b> and <b>Assignments</b>, connect your E-class password using <b>🎓 E-class</b>."
    )


def must_register_with_password() -> str:
    return (
        "⚠️ You already used this bot with a different account.\n\n"
        "For security, please enter your <b>E-class password</b> to connect your account."
    )


def ask_password(student_id: str) -> str:
    return (
        f"🔐 Please enter your <b>E-class password</b> for <b>{student_id}</b>.\n\n"
        "ℹ️ This is not an official E-class bot. "
        "If you do not feel comfortable, please use the official website instead.\n\n"
        "🤝 Your password will not be shared with third parties."
    )


def connecting_eclass() -> str:
    return "⏳ Connecting to E-class… please wait."


def eclass_done(detail: str) -> str:
    return (
        f"{detail}\n\n"
        "✅ Done. Please press <b>Start again</b> (or type /start)."
    )


def timetable_title(first_name: Optional[str], group_name: Optional[str]) -> str:
    fn = first_name or "Student"
    gn = group_name or "-"
    return f"📅 <b>{fn}</b> — Group: <b>{gn}</b>\n\n"


def attendance_title(first_name: Optional[str], last_name: Optional[str], student_id: Optional[str]) -> str:
    full = " ".join([x for x in [first_name, last_name] if x]) or "Student"
    sid = student_id or "-"
    return f"📊 <b>Attendance</b>\n<b>{full}</b> ({sid})\n\n"


def assignments_title(first_name: Optional[str], last_name: Optional[str], student_id: Optional[str]) -> str:
    full = " ".join([x for x in [first_name, last_name] if x]) or "Student"
    sid = student_id or "-"
    return f"📝 <b>Assignments</b>\n<b>{full}</b> ({sid})\n\n"


def no_pending_assignments() -> str:
    return "🎉 No pending assignments. Nice!"


def help_text() -> str:
    return (
        "🆘 <b>What INS Grades does for you</b>\n\n"
        "📝 <b>Assignments</b>\n"
        "• Smart reminders before deadline\n"
        "• Alert if not submitted\n\n"
        "🧾 <b>Grades</b>\n"
        "• Get notified as soon as grades are published\n\n"
        "📊 <b>Attendance</b>\n"
        "• Instant alert for absence or late\n\n"
        "📅 <b>Timetable</b>\n"
        "• Daily plan at 08:00\n"
        "• 30-min class reminder\n\n"
        "Use <b>/start</b> anytime."
    )




def about_text() -> str:
    return (
        "ℹ️ <b>INS Grades</b> — your academic assistant.\n\n"
        "We help you stay ahead with:\n"
        "🔔 Assignment reminders\n"
        "🧾 Grade alerts\n"
        "📊 Absence notifications\n"
        "📅 Timetable updates\n\n"
        "Everything automatic.\n"
        "Everything free."
    )


def generic_error() -> str:
    return "⚠️ Something went wrong. Please try again or use /start."
