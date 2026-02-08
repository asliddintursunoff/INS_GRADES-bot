import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import httpx
import asyncio
import re
import dotenv
import os

dotenv.load_dotenv()

# -----------------------------
# Config
# -----------------------------
API_BASE = os.environ.get("API_BASE")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

# -----------------------------
# Helper functions
# -----------------------------
async def check_user_exists(telegram_id: str) -> bool:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{API_BASE}/user/is-exist",
            params={"telegram_id": telegram_id}
        )
        r.raise_for_status()
        return r.json()

async def register_user(telegram_id: str, student_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{API_BASE}/user/register-user",
            json={
                "telegram_id": telegram_id,
                "student_id": student_id
            }
        )
        r.raise_for_status()
        return r.json()

async def get_my_timetable(telegram_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{API_BASE}/my-timetable",
            params={"telegram_id": telegram_id}
        )
        r.raise_for_status()
        return r.json()

# -----------------------------
# Timetable Formatter
# -----------------------------
def format_timetable_pretty(data: dict) -> str:
    # safer name fallback (avoids "None")
    user_name = (
        data.get("user_first_name")
        or data.get("user_name")
        or "Student"
    )
    group_name = data.get("group") or "Your Group"
    timetable = data.get("time_table", [])

    if not timetable:
        return (
            f"👋 <b>Hello, {user_name}!</b>\n\n"
            "🎉 <i>You don’t have any classes scheduled this week.</i>\n"
            "Go touch grass 🌿 (or code something cool) 😄"
        )

    weekdays_order = [
        "monday", "tuesday", "wednesday",
        "thursday", "friday", "saturday", "sunday"
    ]

    timetable_by_day = {day: [] for day in weekdays_order}
    for cls in timetable:
        day = (cls.get("week_day") or "").lower()
        if day in timetable_by_day:
            timetable_by_day[day].append(cls)

    lines = [
        f"👋 <b>Hello, {user_name}!</b>",
        f"🎓 <b>Group:</b> <i>{group_name}</i>",
        ""
    ]

    # “tabs” using indentation + bullets + tree style
    IND = "   "  # 3 spaces
    for day in weekdays_order:
        day_classes = timetable_by_day[day]
        if not day_classes:
            continue

        day_classes.sort(key=lambda x: x.get("start_time", ""))
        lines.append(f"📅 <b>{day.capitalize()}</b>")

        for cls in day_classes:
            start = (cls.get("start_time") or "")[:5]
            end = (cls.get("end_time") or "")[:5]
            subject = cls.get("subject") or "Unknown subject"
            room = cls.get("room") or "TBA"

            # One compact “subclass card”
            lines.append(
                f"{IND}├─ ⏰ <b>{start}–{end}</b>  •  📘 <b>{subject}</b>\n"
                f"{IND}│    🏫 <i>{room}</i>"
            )

        lines.append("")  # blank line between days

    lines.append("✅ <i>Have a great and productive week!</i> 💪📚")
    return "\n".join(lines)


# -----------------------------
# Bot Handlers
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)
    context.user_data.clear()

    try:
        exists = await check_user_exists(telegram_id)
    except Exception:
        await update.message.reply_text(
            "🚫 <b>Oops!</b>\n\n"
            "Our server is temporarily unavailable.\n"
            "Please try again in a few minutes.",
            parse_mode="HTML"
        )
        return

    if exists:
        await send_timetable_keyboard(update)
    else:
        context.user_data["registering"] = True
        await update.message.reply_text(
            "👋 <b>Welcome!</b>\n\n"
            "To get started, please enter your <b>Student ID</b>.\n\n"
            "📌 <i>Format:</i> <code>U2510232</code>\n"
            "• Starts with <b>U</b> or <b>B</b>\n"
            "• Followed by <b>7 digits</b>",
            parse_mode="HTML"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)
    text = update.message.text.strip()

    # ---------------- Registration ----------------
    if context.user_data.get("registering"):
        student_id = text.upper()

        if not re.fullmatch(r"[UB]\d{7}", student_id):
            await update.message.reply_text(
                "❌ <b>Invalid Student ID</b>\n\n"
                "Please use this format:\n"
                "📌 <code>U2510232</code>\n\n"
                "Try again 👇",
                parse_mode="HTML"
            )
            return

        try:
            await register_user(telegram_id, student_id)
        except httpx.HTTPStatusError:
            await update.message.reply_text(
                "⚠️ <b>Student ID not found</b>\n\n"
                "Please double-check your ID and try again.",
                parse_mode="HTML"
            )
            return
        except Exception:
            await update.message.reply_text(
                "🚫 <b>Registration failed</b>\n\n"
                "Something went wrong. Please type /start to try again.",
                parse_mode="HTML"
            )
            context.user_data.clear()
            return

        context.user_data.clear()
        await update.message.reply_text(
    "✅ <b>Registration successful!</b>\n\n"
    "🎒 <b>What this bot can do for you:</b>\n"
    "• 📅 Show your timetable anytime\n"
    "• 🌞 <b>Every morning at 08:00</b> it sends <i>today’s classes</i>\n"
    "• ⏰ <b>30 minutes before each class</b> it reminds you so you don’t get cooked 😅\n\n"
    "💡 <i>Pro tip:</i> If you ignore the reminders, at least don’t ignore attendance 😄",
    parse_mode="HTML"
)

        await send_timetable_keyboard(update)
        return

    # ---------------- My Timetable ----------------
    if text == "📅 My Timetable":
        try:
            exists = await check_user_exists(telegram_id)
        except Exception:
            await update.message.reply_text(
                "🚫 <b>Server error</b>\n\n"
                "Please type /start to continue.",
                parse_mode="HTML",
                reply_markup=ReplyKeyboardRemove()
            )
            context.user_data.clear()
            return

        if not exists:
            await update.message.reply_text(
                "⚠️ <b>Your data was not found</b>\n\n"
                "Please type /start to register again.",
                parse_mode="HTML",
                reply_markup=ReplyKeyboardRemove()
            )
            context.user_data.clear()
            return

        msg = await update.message.reply_text(
            "⏳ <i>Fetching your timetable…</i>",
            parse_mode="HTML"
        )

        try:
            data = await get_my_timetable(telegram_id)
        except Exception:
            await msg.edit_text(
                "❌ <b>Failed to load timetable</b>\n\n"
                "Please try again in a moment.",
                parse_mode="HTML"
            )
            return

        await msg.edit_text(
            format_timetable_pretty(data),
            parse_mode="HTML"
        )
        return

    # ---------------- Fallback ----------------
    await update.message.reply_text(
        "ℹ️ <b>What would you like to do?</b>\n\n"
        "• Tap <b>📅 My Timetable</b>\n"
        "• Or type /start to begin",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )

# -----------------------------
# Keyboard
# -----------------------------
async def send_timetable_keyboard(update: Update):
    keyboard = [[KeyboardButton("📅 My Timetable")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "👇 <b>Quick Access</b>\n\n"
        "Tap the button below anytime to view your timetable:",
        parse_mode="HTML",
        reply_markup=reply_markup
    )

# -----------------------------
# Run Bot
# -----------------------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(app.run_polling())
    except RuntimeError:
        asyncio.run(app.run_polling())
