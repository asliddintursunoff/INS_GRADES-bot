from __future__ import annotations

from typing import Optional

def intro(first_name: str | None, user_type: str) -> str:
    name = first_name or "there"

    lines = [
        f"👋 Hi <b>{name}</b>!",
        "",
        "Welcome to <b>INS Grades</b> 🎓",
        "Here’s what I can do for you:",
        "• 📅 Show your timetable",
        "• ⏰ Send today’s classes at <b>08:00</b>",
        "• 🔔 Remind you <b>30 minutes</b> before each class (with absence count)",
    ]

    if user_type == "new_user":
        lines += [
            "",
            "To get started, please register your <b>Student ID</b> 🆕",
        ]
    elif user_type == "half_user":
        lines += [
            "",
            "To unlock assignments, attendance, grades, and quizzes:",
            "🎓 Please connect your <b>E-class</b> from the menu.",
        ]
    else:  # full_user
        lines += [
            "",
            "You also have access to:",
            "• 📝 Assignments + smart due reminders",
            "• 📊 Attendance + absence/late alerts",
            "• 🧾 Grade notifications",
            "• 🧩 Quiz updates",

            "<b>\n🔔 We will send you a notification as soon as something new is added during the day!</b>\n\n",
"📌 To make sure you don’t miss any updates, please <b>pin this chat</b> and <b>unmute</b>in Telegram so it stays at the top of your list."

        ]

    lines += [
        "",
        "✅ Everything is free for you.",
    ]

    return "\n".join(lines)


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
        "🆘 <b>Help</b>\n\n"
        "Use <b>/start</b> to open the menu anytime.\n\n"
        "✨ What you can do here:\n"
        "📅 <b>Timetable</b> — see your weekly schedule\n"
        "⏰ <b>Daily class plan</b> — every morning at 08:00 you’ll get today’s classes\n"
        "🔔 <b>Class reminders</b> — a reminder 30 minutes before each class (with absence count)\n\n"
        "🎓 <b>E-class</b> (connect once to unlock more):\n"
        "📝 <b>Assignments</b> — see what’s due soon and what’s not submitted\n"
        "📌 <b>Smart alerts</b> — notifications at 5 days, 3 days, 1 day, and on the due date\n"
        "🧾 <b>Grades</b> — get a message when your grades are published\n"
        "🧩 <b>Quizzes</b> — get updates about quizzes\n"
        "📊 <b>Attendance</b> — get alerts for absence/late and view your stats\n\n"
        "✅ Everything is free for you.\n\n"
        "Commands:\n"
        "• /start — open menu\n"
        "• /help — show this help\n"
        "• /about — about the bot"
    )



def about_text() -> str:
    return (
        "ℹ️ <b>About INS Grades</b>\n\n"
        "👤 Bot: <b>@ins_gradesbot</b>\n\n"
        "INS Grades helps you stay on top of your study life:\n"
        "📅 timetable, ⏰ reminders, 📝 assignments, 📊 attendance, 🧾 grades, and 🧩 quizzes.\n\n"
        "🔔 Notifications you’ll get:\n"
        "• new assignment added\n"
        "• assignment not submitted (5 days, 3 days, 1 day, due day)\n"
        "• new grades published\n"
        "• quiz updates\n"
        "• attendance changes (absence/late)\n\n"
        "✅ Everything is free for you.\n"
        "If you ever feel unsure, you can always use the official website instead."
    )

def generic_error() -> str:
    return "⚠️ Something went wrong. Please try again or use /start."
