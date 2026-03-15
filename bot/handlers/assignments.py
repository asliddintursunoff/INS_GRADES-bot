from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message
from bot.api_client import APIClient
from bot.texts import messages
from bot.keyboards.main_menu import get_main_menu

router = Router()

def format_deadline(deadline_str: str) -> str:
    try:
        # 2026-03-16T08:00:00 -> 16 Mar 08:00
        # Use strptime to handle potentially varied formats if needed, but ISO is standard
        dt = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))

        # Mapping for months to be more user friendly if we want 'Mar'
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month_name = months[dt.month - 1]

        return f"{dt.day} {month_name} {dt.strftime('%H:%M')}"
    except (ValueError, TypeError, IndexError):
        return deadline_str

@router.message(F.text == messages.BTN_ASSIGNMENTS)
async def handle_assignments(message: Message, api_client: APIClient):
    telegram_id = message.from_user.id
    data = await api_client.get_assignments(telegram_id)

    if not data:
        await message.answer(messages.ASSIGNMENTS_ERROR, parse_mode="HTML")
        return

    response_text = messages.ASSIGNMENTS_HEADER

    # API returns unified list sometimes, but let's check both
    items = []
    if isinstance(data, dict):
        items = data.get("assignments", []) + data.get("quizzes", [])
    elif isinstance(data, list):
        items = data

    for item in items:
        raw_type = item.get("type", "Assignment")
        display_type = raw_type.capitalize()

        response_text += messages.ASSIGNMENT_ITEM.format(
            subject_name=item.get("subject_name", "Unknown Subject"),
            name=item.get("name", "Unnamed Task"),
            type=display_type,
            deadline=format_deadline(item.get("deadline", "")),
            time_left=item.get("time_left", ""),
            url=item.get("url", "#")
        )

    user = await api_client.get_user(telegram_id)
    is_subscribed = user.get("is_subscribed", False) if user else True

    await message.answer(response_text, reply_markup=get_main_menu(is_subscribed), parse_mode="HTML", disable_web_page_preview=True)
