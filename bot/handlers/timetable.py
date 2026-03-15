from aiogram import Router, F
from aiogram.types import Message
from bot.api_client import APIClient
from bot.texts import messages
from bot.keyboards.main_menu import get_main_menu

router = Router()

def clean_time(time_str: str) -> str:
    # 09:30:00 -> 09:30
    if not time_str: return ""
    parts = time_str.split(":")
    if len(parts) >= 2:
        return f"{parts[0]}:{parts[1]}"
    return time_str

@router.message(F.text == messages.BTN_TIMETABLE)
async def handle_timetable(message: Message, api_client: APIClient):
    telegram_id = message.from_user.id
    timetable_data = await api_client.get_timetable(telegram_id)
    user = await api_client.get_user(telegram_id)

    if not timetable_data or not user:
        await message.answer(messages.TIMETABLE_ERROR, parse_mode="HTML")
        return

    first_name = user.get("first_name", "")
    student_id = user.get("student_id", "")

    response_text = messages.TIMETABLE_HEADER.format(name=first_name, group=student_id)

    if isinstance(timetable_data, dict):
        for day, sessions in timetable_data.items():
            if not sessions: continue
            response_text += messages.TIMETABLE_DAY_HEADER.format(day=day.capitalize())
            for session in sessions:
                # API might return subject as a string or a dict.
                # If it's showing "Unknown", let's look for common keys.
                raw_subject = session.get("subject")
                subject_name = "Unknown"

                if isinstance(raw_subject, dict):
                    # Check common keys in API response
                    subject_name = raw_subject.get("name") or raw_subject.get("subject_name") or str(raw_subject)
                elif raw_subject:
                    subject_name = str(raw_subject)

                # Sometimes subject name is directly in session
                if subject_name == "Unknown":
                    subject_name = session.get("subject_name") or session.get("name") or "Unknown"

                # Calculate abbreviation
                abbr = "".join([w[0] for w in subject_name.split() if w and w[0].isupper()])[:3]
                if not abbr: abbr = subject_name[:1].upper() or "U"

                response_text += messages.TIMETABLE_ITEM.format(
                    start_time=clean_time(session.get("start_time", "")),
                    end_time=clean_time(session.get("end_time", "")),
                    abbr=abbr,
                    subject=subject_name,
                    room=session.get("room", "")
                )

    is_subscribed = user.get("is_subscribed", False)
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
