from aiogram import Router, F
from aiogram.types import CallbackQuery
from bot.api_client import APIClient
from bot.texts import messages
from bot.keyboards.main_menu import get_main_menu

router = Router()

@router.callback_query(F.data == "assignments")
async def handle_assignments(callback: CallbackQuery, api_client: APIClient):
    telegram_id = callback.from_user.id
    data = await api_client.get_assignments(telegram_id)

    if not data:
        await callback.answer(messages.ASSIGNMENTS_ERROR, show_alert=True)
        return

    response_text = f"{messages.ASSIGNMENTS_HEADER}\n"

    assignments = data.get("assignments", [])
    for item in assignments:
        response_text += messages.ASSIGNMENT_ITEM.format(
            subject=item.get("subject", ""),
            task=item.get("task", ""),
            deadline=item.get("deadline", ""),
            time_left=item.get("time_left", ""),
            url=item.get("url", "")
        )

    quizzes = data.get("quizzes", [])
    if quizzes:
        response_text += messages.QUIZZES_SUBHEADER
        for item in quizzes:
            response_text += messages.QUIZ_ITEM.format(
                subject=item.get("subject", ""),
                title=item.get("title", ""),
                deadline=item.get("deadline", ""),
                time_left=item.get("time_left", ""),
                url=item.get("url", "")
            )

    user = await api_client.get_user(telegram_id)
    is_subscribed = user.get("is_subscribed", False) if user else True

    await callback.message.answer(response_text, reply_markup=get_main_menu(is_subscribed))
    await callback.answer()
