from aiogram import Router, F
from aiogram.types import Message
from bot.api_client import APIClient
from bot.texts import messages
from bot.keyboards.main_menu import get_main_menu

router = Router()

@router.message(F.text == messages.BTN_ASSIGNMENTS)
async def handle_assignments(message: Message, api_client: APIClient):
    telegram_id = message.from_user.id
    data = await api_client.get_assignments(telegram_id)

    if not data:
        await message.answer(messages.ASSIGNMENTS_ERROR, parse_mode="HTML")
        return

    response_text = messages.ASSIGNMENTS_HEADER

    assignments = data.get("assignments", [])
    for item in assignments:
        response_text += messages.ASSIGNMENT_ITEM.format(
            subject=item.get("subject", ""),
            type="Assignment",
            deadline=item.get("deadline", ""),
            time_left=item.get("time_left", ""),
            url=item.get("url", "")
        )

    quizzes = data.get("quizzes", [])
    for item in quizzes:
        response_text += messages.ASSIGNMENT_ITEM.format(
            subject=item.get("subject", ""),
            type="Quiz",
            deadline=item.get("deadline", ""),
            time_left=item.get("time_left", ""),
            url=item.get("url", "")
        )

    user = await api_client.get_user(telegram_id)
    is_subscribed = user.get("is_subscribed", False) if user else True

    await message.answer(response_text, reply_markup=get_main_menu(is_subscribed), parse_mode="HTML", disable_web_page_preview=True)
