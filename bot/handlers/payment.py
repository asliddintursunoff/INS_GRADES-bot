from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.api_client import APIClient
from bot.texts import messages
from bot.keyboards.back import get_back_keyboard
from bot.keyboards.main_menu import get_main_menu

router = Router()

class PaymentStates(StatesGroup):
    waiting_for_receipt = State()

@router.callback_query(F.data == "buy_premium")
async def buy_premium_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        messages.PREMIUM_INFO.format(price="10"), # Example price
        reply_markup=get_back_keyboard()
    )
    await state.set_state(PaymentStates.waiting_for_receipt)
    await callback.answer()

@router.message(PaymentStates.waiting_for_receipt, F.photo)
async def process_receipt(message: Message, state: FSMContext, api_client: APIClient, bot: Bot):
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)

    # Download file
    file_bytes = await bot.download_file(file_info.file_path)

    # file_bytes is a BytesIO object.
    # The reviewer said calling .read() without .seek(0) might return empty if cursor is at end.
    # Actually, bot.download_file returns a BytesIO and typically it's at 0 or we can just call getValue()
    content = file_bytes.getvalue()

    telegram_id = message.from_user.id
    success = await api_client.check_payment(telegram_id, content, f"receipt_{telegram_id}.jpg")

    if success:
        await message.answer(messages.PAYMENT_SUCCESS)
        user = await api_client.get_user(telegram_id)
        is_subscribed = user.get("is_subscribed", False) if user else True
        await message.answer(messages.MAIN_MENU_LABEL, reply_markup=get_main_menu(is_subscribed))
        await state.clear()
    else:
        await message.answer(messages.PAYMENT_FAILED, reply_markup=get_back_keyboard())

@router.message(PaymentStates.waiting_for_receipt, ~F.photo)
async def not_a_photo(message: Message):
    await message.answer(messages.PAYMENT_ASK_PHOTO)
