from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.api_client import APIClient
from bot.texts import messages
from bot.keyboards.main_menu import get_main_menu

router = Router()

def format_deadline(deadline_str: str) -> str:
    try:
        dt = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month_name = months[dt.month - 1]
        return f"{dt.day} {month_name} {dt.strftime('%H:%M')}"
    except (ValueError, TypeError, IndexError):
        return deadline_str

async def check_registration(message: Message, api_client: APIClient, state: FSMContext) -> bool:
    user = await api_client.get_user(message.from_user.id)
    if not user:
        from bot.handlers.start import RegistrationStates
        await message.answer(messages.NOT_REGISTERED, parse_mode="HTML")
        await message.answer(messages.ASK_STUDENT_ID, parse_mode="HTML")
        await state.set_state(RegistrationStates.waiting_for_student_id)
        return False
    return True

@router.message(F.text == messages.BTN_ASSIGNMENTS)
async def handle_assignments(message: Message, api_client: APIClient, state: FSMContext):
    if not await check_registration(message, api_client, state):
        return

    data = await api_client.get_assignments(message.from_user.id)

    if not data:
        await message.answer(messages.ASSIGNMENTS_ERROR, parse_mode="HTML")
        return

    response_text = messages.ASSIGNMENTS_HEADER

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

    user = await api_client.get_user(message.from_user.id)
    is_subscribed = user.get("is_subscribed", False) if user else True

    await message.answer(response_text, reply_markup=get_main_menu(is_subscribed), parse_mode="HTML", disable_web_page_preview=True)
