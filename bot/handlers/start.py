from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.api_client import APIClient
from bot.texts import messages
from bot.keyboards.main_menu import get_main_menu

router = Router()

class RegistrationStates(StatesGroup):
    waiting_for_student_id = State()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext, api_client: APIClient):
    await state.clear()
    telegram_id = message.from_user.id
    user = await api_client.get_user(telegram_id)

    if user:
        await show_main_menu(message, user)
    else:
        await message.answer(messages.ASK_STUDENT_ID)
        await state.set_state(RegistrationStates.waiting_for_student_id)

@router.message(RegistrationStates.waiting_for_student_id)
async def process_student_id(message: Message, state: FSMContext, api_client: APIClient):
    student_id = message.text
    telegram_id = message.from_user.id

    success = await api_client.register_user(telegram_id, student_id)
    if success:
        user = await api_client.get_user(telegram_id)
        if user:
            await message.answer(messages.REGISTRATION_SUCCESS, parse_mode="HTML")
            await show_main_menu(message, user)
            await state.clear()
        else:
            await message.answer("Error retrieving user.")
    else:
        await message.answer("Registration failed.")

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
