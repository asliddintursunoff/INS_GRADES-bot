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
            await message.answer(messages.REGISTRATION_ERROR_RETRIEVING, parse_mode="HTML")
    else:
        await message.answer(messages.REGISTRATION_FAILED, parse_mode="HTML")

async def show_main_menu(message: Message, user: dict):
    first_name = user.get("first_name", "")
    last_name = user.get("last_name", "")
    is_subscribed = user.get("is_subscribed", False)

    plan_info = messages.PREMIUM_USER if is_subscribed else messages.FREE_USER
    upgrade_info = "" if is_subscribed else messages.UPGRADE_PROMPT

    full_message = messages.START_HELLO.format(
        first_name=first_name,
        last_name=last_name,
        plan_info=plan_info,
        upgrade_info=upgrade_info
    )
    await message.answer(full_message, reply_markup=get_main_menu(is_subscribed), parse_mode="HTML")
