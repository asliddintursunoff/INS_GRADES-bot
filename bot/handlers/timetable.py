from aiogram import Router, F
from aiogram.types import CallbackQuery
from bot.api_client import APIClient
from bot.texts import messages
from bot.keyboards.main_menu import get_main_menu

router = Router()

@router.callback_query(F.data == "timetable")
async def handle_timetable(callback: CallbackQuery, api_client: APIClient):
    telegram_id = callback.from_user.id
    timetable_data = await api_client.get_timetable(telegram_id)

    if not timetable_data:
        await callback.answer(messages.TIMETABLE_ERROR, show_alert=True)
        return

    response_text = f"{messages.TIMETABLE_HEADER}\n"

    if isinstance(timetable_data, dict):
        for day, sessions in timetable_data.items():
            if not sessions: continue
            response_text += f"\n📅 {day.upper()}\n"
            for session in sessions:
                response_text += messages.TIMETABLE_ITEM.format(
                    start_time=session.get("start_time", ""),
                    end_time=session.get("end_time", ""),
                    subject=session.get("subject", ""),
                    professor=session.get("professor", ""),
                    room=session.get("room", "")
                )

    user = await api_client.get_user(telegram_id)
    is_subscribed = user.get("is_subscribed", False) if user else False

    await callback.message.answer(response_text, reply_markup=get_main_menu(is_subscribed))
    await callback.answer()

@router.callback_query(F.data == "back_to_main")
async def handle_back_to_main(callback: CallbackQuery, api_client: APIClient):
    telegram_id = callback.from_user.id
    user = await api_client.get_user(telegram_id)

    if user:
        is_subscribed = user.get("is_subscribed", False)
        plan_info = messages.PREMIUM_USER if is_subscribed else messages.FREE_USER
        await callback.message.edit_text(plan_info, reply_markup=get_main_menu(is_subscribed))
    else:
        await callback.message.edit_text(messages.SESSION_EXPIRED)

    await callback.answer()
