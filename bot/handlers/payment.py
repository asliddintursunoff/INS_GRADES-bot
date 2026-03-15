import os
from aiogram import Router, F, Bot
from aiogram.types import Message, FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.api_client import APIClient
from bot.texts import messages
from bot.keyboards.back import get_back_keyboard
from bot.keyboards.main_menu import get_main_menu

router = Router()

class PaymentStates(StatesGroup):
    waiting_for_receipt = State()

async def check_registration(message: Message, api_client: APIClient, state: FSMContext) -> bool:
    user = await api_client.get_user(message.from_user.id)
    if not user:
        from bot.handlers.start import RegistrationStates
        await message.answer(messages.NOT_REGISTERED, parse_mode="HTML")
        await message.answer(messages.ASK_STUDENT_ID, parse_mode="HTML")
        await state.set_state(RegistrationStates.waiting_for_student_id)
        return False
    return True

@router.message(F.text == messages.BTN_BUY_PREMIUM)
async def buy_premium_handler(message: Message, state: FSMContext, api_client: APIClient):
    if not await check_registration(message, api_client, state):
        return

    # Send example images first
    path1 = "bot/assets/1.jpg"
    path2 = "bot/assets/2.jpg"

    if os.path.exists(path1) and os.path.exists(path2):
        media = [
            InputMediaPhoto(
                media=FSInputFile(path1),
                caption=messages.RECEIPT_EXAMPLE_TEXT,
                parse_mode="HTML"
            ),
            InputMediaPhoto(media=FSInputFile(path2))
        ]
        await message.answer_media_group(media=media)
    else:
        await message.answer(messages.RECEIPT_EXAMPLE_TEXT, parse_mode="HTML")

    # Send activation message later
    await message.answer(
        messages.PREMIUM_ACTIVATION,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )

    await state.set_state(PaymentStates.waiting_for_receipt)

@router.message(PaymentStates.waiting_for_receipt, F.photo)
async def process_receipt(message: Message, state: FSMContext, api_client: APIClient, bot: Bot):
    waiting_msg = await message.answer(messages.PAYMENT_WAITING, parse_mode="HTML")

    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    file_bytes = await bot.download_file(file_info.file_path)

    telegram_id = message.from_user.id
    success, resp_data = await api_client.check_payment(telegram_id, file_bytes.getvalue(), f"receipt_{telegram_id}.jpg")

    try:
        await waiting_msg.delete()
    except:
        pass

    if success:
        await message.answer(messages.PAYMENT_SUCCESS, reply_markup=get_main_menu(True), parse_mode="HTML")
        await state.clear()
    else:
        error_details = ""
        if isinstance(resp_data, dict) and "detail" in resp_data:
            error_details = resp_data["detail"]
        elif isinstance(resp_data, str):
            error_details = resp_data

        await message.answer(
            messages.PAYMENT_ERROR.format(error_details=error_details),
            reply_markup=get_back_keyboard(),
            parse_mode="HTML"
        )

@router.message(PaymentStates.waiting_for_receipt, ~F.photo)
async def not_a_photo(message: Message, api_client: APIClient, state: FSMContext):
    if message.text == messages.BTN_BACK:
        await state.clear()
        user = await api_client.get_user(message.from_user.id)
        if user:
            from bot.handlers.start import show_main_menu
            await show_main_menu(message, user)
        else:
            if not await check_registration(message, api_client, state):
                return
        return
    await message.answer(messages.PAYMENT_ASK_PHOTO)
