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
        r = await client.get(f"{API_BASE}/user/is-exist", params={"telegram_id": telegram_id})
        r.raise_for_status()
        return r.json()

async def register_user(telegram_id: str, student_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{API_BASE}/user/register-user", json={
            "telegram_id": telegram_id,
            "student_id": student_id
        })
        r.raise_for_status()
        return r.json()

async def get_my_timetable(telegram_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_BASE}/my-timetable", params={"telegram_id": telegram_id})
        r.raise_for_status()
        return r.json()

# -----------------------------
# Timetable Formatter
# -----------------------------
def format_timetable_pretty(data: dict) -> str:
    user_name = data.get("user_first_name", "Student")
    group_name = data.get("group", "Your Group")
    timetable = data.get("time_table", [])

    if not timetable:
        return f"Hello, {user_name} 👋\n\nYou have no classes scheduled this week. Enjoy! 😊"

    weekdays_order = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    timetable_by_day = {day: [] for day in weekdays_order}

    for cls in timetable:
        day = cls["week_day"].lower()
        if day in timetable_by_day:
            timetable_by_day[day].append(cls)

    lines = [
        f"Hello, {user_name} 👋",
        f"🎓 <b>{group_name}</b>\n"
    ]

    for day in weekdays_order:
        day_classes = timetable_by_day[day]
        if not day_classes:
            continue

        day_classes.sort(key=lambda x: x["start_time"])
        lines.append(f"📅 <b>{day.capitalize()}</b>:")

        for cls in day_classes:
            start = cls["start_time"][:5]
            end = cls["end_time"][:5]
            subject = cls["subject"]
            room = cls["room"]
            # Minimalist, readable
            lines.append(f"• <b>{subject}</b> — <i>{start}-{end}</i> — {room}")

        lines.append("")  # blank line between days

    lines.append("✅ Have a productive week!")
    return "\n".join(lines)

# -----------------------------
# Bot Handlers
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)
    context.user_data.clear()  # reset all previous states

    try:
        exists = await check_user_exists(telegram_id)
    except Exception:
        await update.message.reply_text("❌ Backend error. Please try /start again later.")
        return

    if exists:
        await send_timetable_keyboard(update)
    else:
        context.user_data["registering"] = True
        await update.message.reply_text(
            "Welcome! Please enter your student ID to register.\n"
            "It should start with U/u or B/b followed by 7 digits (e.g., U2510232)."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)
    text = update.message.text.strip()

    # ---------------- Registration ----------------
    if context.user_data.get("registering"):
        student_id = text.upper()
        if not re.fullmatch(r"[UB]\d{7}", student_id):
            await update.message.reply_text(
                "❌ Invalid student ID format. Must start with U/u or B/b + 7 digits (e.g., U2510232). Please try again:"
            )
            return

        try:
            user = await register_user(telegram_id, student_id)
        except httpx.HTTPStatusError:
            await update.message.reply_text("❌ Student ID incorrect. Please try again:")
            return
        except Exception:
            await update.message.reply_text("❌ Server error. Please click /start again.")
            context.user_data["registering"] = False
            return

        context.user_data["registering"] = False
        await update.message.reply_text("✅ Registration successful!")
        await send_timetable_keyboard(update)
        return

    # ---------------- My Timetable ----------------
    if text == "📅 My Timetable":
        # Validate user still exists
        try:
            exists = await check_user_exists(telegram_id)
        except Exception:
            await update.message.reply_text(
                "❌ Backend error. Please click /start again.",
                reply_markup=ReplyKeyboardRemove()
            )
            context.user_data.clear()
            return

        if not exists:
            await update.message.reply_text(
                "⚠️ Your data was not found. Please click /start to register again.",
                reply_markup=ReplyKeyboardRemove()
            )
            context.user_data.clear()
            return

        msg = await update.message.reply_text("⏳ Fetching your timetable, please wait...")

        try:
            data = await get_my_timetable(telegram_id)
        except Exception:
            await msg.edit_text("❌ Failed to fetch timetable. Please click 'My Timetable' again.")
            return

        # Format timetable beautifully
        formatted = format_timetable_pretty(data)
        await msg.edit_text(formatted, parse_mode="HTML")
        return

    # ---------------- Fallback ----------------
    await update.message.reply_text(
        "Please click /start to begin or press 'My Timetable'.",
        reply_markup=ReplyKeyboardRemove()
    )

# -----------------------------
# Keyboard
# -----------------------------
async def send_timetable_keyboard(update: Update):
    keyboard = [[KeyboardButton("📅 My Timetable")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "✅ You can now get your timetable anytime using the button below:",
        reply_markup=reply_markup
    )

# -----------------------------
# Run Bot
# -----------------------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # VS Code / interactive loop safe
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(app.run_polling())
    except RuntimeError:
        asyncio.run(app.run_polling())
