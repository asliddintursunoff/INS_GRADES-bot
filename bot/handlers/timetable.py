from aiogram import Router, F
from aiogram.types import Message
from bot.api_client import APIClient
from bot.texts import messages
from bot.keyboards.main_menu import get_main_menu

router = Router()

@router.message(F.text == messages.BTN_TIMETABLE)
async def handle_timetable(message: Message, api_client: APIClient):
    telegram_id = message.from_user.id
    timetable_data = await api_client.get_timetable(telegram_id)

    if not timetable_data:
        await message.answer(messages.TIMETABLE_ERROR, parse_mode="HTML")
        return

    response_text = f"{messages.TIMETABLE_HEADER}\n"

    if isinstance(timetable_data, dict):
        for day, sessions in timetable_data.items():
            if not sessions: continue
            response_text += messages.TIMETABLE_DAY_HEADER.format(day=day.capitalize())
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

    await message.answer(response_text, reply_markup=get_main_menu(is_subscribed), parse_mode="HTML")

@router.message(F.text == messages.BTN_BACK)
async def handle_back_to_main(message: Message, api_client: APIClient):
    telegram_id = message.from_user.id
    user = await api_client.get_user(telegram_id)

    if user:
        from bot.handlers.start import show_main_menu
        await show_main_menu(message, user)
    else:
        await message.answer(messages.SESSION_EXPIRED, parse_mode="HTML")
