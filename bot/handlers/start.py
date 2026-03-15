import re
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.api_client import APIClient
from bot.texts import messages
from bot.keyboards.main_menu import get_main_menu

router = Router()

class RegistrationStates(StatesGroup):
    waiting_for_student_id = State()
    confirming_id = State()

def get_confirmation_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=messages.BTN_YES), KeyboardButton(text=messages.BTN_NO)]
        ],
        resize_keyboard=True
    )

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext, api_client: APIClient):
    await state.clear()
    telegram_id = message.from_user.id
    user = await api_client.get_user(telegram_id)

    if user:
        await show_main_menu(message, user)
    else:
        await message.answer(messages.START_MESSAGE, parse_mode="HTML")
        await message.answer(messages.ASK_STUDENT_ID, parse_mode="HTML")
        await state.set_state(RegistrationStates.waiting_for_student_id)

@router.message(RegistrationStates.waiting_for_student_id)
async def process_student_id(message: Message, state: FSMContext):
    student_id = message.text.strip().upper()

    # Validate format: U + 7 digits
    if not re.match(r"^U\d{7}$", student_id):
        await message.answer(messages.INVALID_STUDENT_ID, parse_mode="HTML")
        return

    await state.update_data(student_id=student_id)
    await message.answer(
        messages.CONFIRM_REGISTRATION.format(student_id=student_id),
        reply_markup=get_confirmation_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(RegistrationStates.confirming_id)

@router.message(RegistrationStates.confirming_id)
async def confirm_registration(message: Message, state: FSMContext, api_client: APIClient):
    if message.text == messages.BTN_YES:
        data = await state.get_data()
        student_id = data.get("student_id")
        telegram_id = message.from_user.id

        success = await api_client.register_user(telegram_id, student_id)
        if success:
            user = await api_client.get_user(telegram_id)
            if user:
                await message.answer(messages.REGISTRATION_SUCCESS, parse_mode="HTML")
                await show_main_menu(message, user)
                await state.clear()
            else:
                await message.answer("Error retrieving user.", reply_markup=get_main_menu(False))
        else:
            await message.answer("Registration failed. Please try /start again.", reply_markup=get_main_menu(False))
            await state.clear()
    else:
        await message.answer(messages.ASK_STUDENT_ID, parse_mode="HTML", reply_markup=get_main_menu(False))
        await state.set_state(RegistrationStates.waiting_for_student_id)

async def show_main_menu(message: Message, user: dict):
    is_subscribed = user.get("is_subscribed", False)

    if not is_subscribed:
        await message.answer(
            messages.START_WELCOME,
            reply_markup=get_main_menu(is_subscribed),
            parse_mode="HTML"
        )
    else:
        first_name = user.get("first_name", "")
        await message.answer(
            f"👋 <b>Welcome back, {first_name}!</b>",
            reply_markup=get_main_menu(is_subscribed),
            parse_mode="HTML"
        )
