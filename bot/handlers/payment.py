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

@router.message(F.text == messages.BTN_BUY_PREMIUM)
async def buy_premium_handler(message: Message, state: FSMContext):
    await message.answer(
        messages.PREMIUM_ACTIVATION,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )

    click_path = "bot/assets/click.jpg"
    payme_path = "bot/assets/payme.jpg"

    if os.path.exists(click_path) and os.path.exists(payme_path):
        media = [
            InputMediaPhoto(
                media=FSInputFile(payme_path),
                caption=messages.RECEIPT_EXAMPLE_TEXT,
                parse_mode="HTML"
            ),
            InputMediaPhoto(media=FSInputFile(click_path))
        ]
        await message.answer_media_group(media=media)
    else:
        # Fallback if images are missing
        await message.answer(messages.RECEIPT_EXAMPLE_TEXT, parse_mode="HTML")

    await state.set_state(PaymentStates.waiting_for_receipt)

@router.message(PaymentStates.waiting_for_receipt, F.photo)
async def process_receipt(message: Message, state: FSMContext, api_client: APIClient, bot: Bot):
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    file_bytes = await bot.download_file(file_info.file_path)

    telegram_id = message.from_user.id
    success = await api_client.check_payment(telegram_id, file_bytes.getvalue(), f"receipt_{telegram_id}.jpg")

    if success:
        await message.answer(messages.PAYMENT_SUCCESS, parse_mode="HTML")
        user = await api_client.get_user(telegram_id)
        is_subscribed = user.get("is_subscribed", False) if user else True
        await message.answer("Main Menu", reply_markup=get_main_menu(is_subscribed), parse_mode="HTML")
        await state.clear()
    else:
        await message.answer(messages.PAYMENT_ERROR, reply_markup=get_back_keyboard(), parse_mode="HTML")

@router.message(PaymentStates.waiting_for_receipt, ~F.photo)
async def not_a_photo(message: Message, api_client: APIClient, state: FSMContext):
    if message.text == messages.BTN_BACK:
        await state.clear()
        telegram_id = message.from_user.id
        user = await api_client.get_user(telegram_id)
        if user:
            from bot.handlers.start import show_main_menu
            await show_main_menu(message, user)
        return
    await message.answer(messages.PAYMENT_ASK_PHOTO)
