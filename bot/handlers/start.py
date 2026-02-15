from __future__ import annotations

from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from bot.config import Settings
from bot.api_client import BackendClient, ApiError
from bot import texts
from bot.keyboards import (
    BTN_BACK,
    confirm_student_id_kb,
    menu_half_user,
    menu_new_user,
    remove_keyboard,
    CB_CONFIRM_ID,
    CB_CHANGE_ID,
    CB_BACK,
)
from bot.states import RegState
from bot.utils import is_valid_student_id, normalize_student_id
from bot.handlers.common import show_main_menu


UD_TEMP_STUDENT_ID = "temp_student_id"
UD_LAST_USER_TYPE = "last_user_type"
UD_REG_NEEDS_ECLASS = "reg_needs_eclass"


async def _send_backend_unavailable(update: Update) -> None:
    chat = update.effective_chat
    if chat:
        await chat.send_message(
            "⚠️ Backend is not responding right now.\nPlease try again in a few seconds.",
            parse_mode="HTML",
            reply_markup=remove_keyboard(),
        )


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    settings: Settings = context.bot_data["settings"]
    telegram_id = str(update.effective_user.id)

    # clear temporary flow data on /start
    context.user_data.pop(UD_TEMP_STUDENT_ID, None)
    context.user_data.pop(UD_REG_NEEDS_ECLASS, None)

    try:
        async with BackendClient(settings.base_url, settings.http_timeout_seconds) as api:
            user_type = await api.get_user_type(telegram_id)
    except ApiError as e:
        if e.status_code == 503:
            await _send_backend_unavailable(update)
            return ConversationHandler.END
        await update.effective_chat.send_message(f"⚠️ {e.detail}", parse_mode="HTML", reply_markup=remove_keyboard())
        return ConversationHandler.END
    except Exception:
        await _send_backend_unavailable(update)
        return ConversationHandler.END

    context.user_data[UD_LAST_USER_TYPE] = user_type

    # show_main_menu() sends intro + keyboard (do not send extra intro here)
    if user_type == "new_user":
        await show_main_menu(update, context, user_type)
        await update.effective_chat.send_message(
            texts.ask_student_id(),
            parse_mode="HTML",
            reply_markup=menu_new_user(),
        )
        return RegState.ASK_STUDENT_ID

    await show_main_menu(update, context, user_type)
    return ConversationHandler.END


async def back_from_new_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.effective_chat.send_message(
        "Okay. Use /start when you’re ready.",
        parse_mode="HTML",
        reply_markup=remove_keyboard(),
    )
    context.user_data.pop(UD_TEMP_STUDENT_ID, None)
    context.user_data.pop(UD_REG_NEEDS_ECLASS, None)
    return ConversationHandler.END


async def on_student_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip()

    if text == BTN_BACK:
        return await back_from_new_user(update, context)

    if not is_valid_student_id(text):
        await update.effective_chat.send_message(texts.invalid_student_id(), parse_mode="HTML")
        return RegState.ASK_STUDENT_ID

    sid = normalize_student_id(text)
    context.user_data[UD_TEMP_STUDENT_ID] = sid

    await update.effective_chat.send_message(
        texts.confirm_student_id(sid),
        parse_mode="HTML",
        reply_markup=confirm_student_id_kb(),
    )
    return RegState.CONFIRM_STUDENT_ID


async def on_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    settings: Settings = context.bot_data["settings"]
    telegram_id = str(update.effective_user.id)

    sid = context.user_data.get(UD_TEMP_STUDENT_ID)
    if not sid:
        await query.edit_message_text(texts.generic_error(), parse_mode="HTML")
        return ConversationHandler.END

    try:
        async with BackendClient(settings.base_url, settings.http_timeout_seconds) as api:
            status, body = await api.register_user(telegram_id=telegram_id, student_id=sid)
    except ApiError as e:
        if e.status_code == 503:
            await query.edit_message_text("⚠️ Backend is not responding. Try again.", parse_mode="HTML")
            return RegState.CONFIRM_STUDENT_ID
        await query.edit_message_text(f"⚠️ {e.detail}", parse_mode="HTML")
        return ConversationHandler.END
    except Exception:
        await query.edit_message_text("⚠️ Backend is not responding. Try again.", parse_mode="HTML")
        return RegState.CONFIRM_STUDENT_ID

    if status == 503:
        await query.edit_message_text("⚠️ Backend is not responding. Try again.", parse_mode="HTML")
        return RegState.CONFIRM_STUDENT_ID

    if status == 200:
        await query.edit_message_text("✅ Student ID confirmed and registered!", parse_mode="HTML")
        await update.effective_chat.send_message(
            texts.registered_half_user(),
            parse_mode="HTML",
            reply_markup=menu_half_user(),
        )
        context.user_data.pop(UD_TEMP_STUDENT_ID, None)
        context.user_data.pop(UD_REG_NEEDS_ECLASS, None)
        context.user_data[UD_LAST_USER_TYPE] = "half_user"
        return ConversationHandler.END

    # status == 300 -> must register with password
    detail = body.get("detail") if isinstance(body, dict) else ""
    if detail.strip().lower() == "user must register with password":
        # continue registration: ask password now, and CLOSE reply buttons
        context.user_data[UD_REG_NEEDS_ECLASS] = True
        await query.edit_message_text(texts.must_register_with_password(), parse_mode="HTML")
        await update.effective_chat.send_message(
            texts.ask_password(sid),
            parse_mode="HTML",
            reply_markup=remove_keyboard(),  # keep closed
        )
        return RegState.ASK_ECLASS_PASSWORD

    msg = detail or f"Unexpected response (status={status})"
    await query.edit_message_text(f"⚠️ {msg}", parse_mode="HTML")
    return ConversationHandler.END


async def on_eclass_password_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    password = (update.message.text or "").strip()

    if password == BTN_BACK:
        return await back_from_new_user(update, context)

    sid = context.user_data.get(UD_TEMP_STUDENT_ID)
    if not sid:
        await update.effective_chat.send_message(texts.generic_error(), parse_mode="HTML", reply_markup=remove_keyboard())
        return ConversationHandler.END

    settings: Settings = context.bot_data["settings"]
    telegram_id = str(update.effective_user.id)

    # keep buttons CLOSED while connecting
    await update.effective_chat.send_message(
        texts.connecting_eclass(),
        parse_mode="HTML",
        reply_markup=remove_keyboard(),
    )

    try:
        async with BackendClient(settings.base_url, settings.http_timeout_seconds) as api:
            resp = await api.register_eclass(telegram_id=telegram_id, student_id=sid, password=password)

    except ApiError as e:
        if e.status_code == 503:
            await update.effective_chat.send_message(
                "⚠️ Backend is not responding right now.\nTry again.",
                parse_mode="HTML",
                reply_markup=remove_keyboard(),
            )
            return RegState.ASK_ECLASS_PASSWORD

        if e.status_code == 403:
            await update.effective_chat.send_message(
                f"❌ {e.detail}\n\n{texts.ask_password(sid)}",
                parse_mode="HTML",
                reply_markup=remove_keyboard(),
            )
            return RegState.ASK_ECLASS_PASSWORD

        await update.effective_chat.send_message(f"⚠️ {e.detail}", parse_mode="HTML", reply_markup=remove_keyboard())
        return ConversationHandler.END
    except Exception:
        await update.effective_chat.send_message(
            "⚠️ Backend is not responding right now.\nTry again.",
            parse_mode="HTML",
            reply_markup=remove_keyboard(),
        )
        return RegState.ASK_ECLASS_PASSWORD

    # ✅ SUCCESS:
    # Backend starts bg task and returns the message we must show to user
    context.user_data.pop(UD_TEMP_STUDENT_ID, None)
    context.user_data.pop(UD_REG_NEEDS_ECLASS, None)

    detail = ""
    if isinstance(resp, dict):
        detail = str(resp.get("detail") or "")

    # Send EXACT backend message, keep keyboard CLOSED
    await update.effective_chat.send_message(
        detail if detail else "✅ Request accepted. Please wait…",
        parse_mode="HTML",
        reply_markup=remove_keyboard(),
    )

    return ConversationHandler.END


async def on_change_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    context.user_data.pop(UD_TEMP_STUDENT_ID, None)

    await query.edit_message_text("✏️ Okay, send your Student ID again.", parse_mode="HTML")
    await update.effective_chat.send_message(
        texts.ask_student_id(),
        parse_mode="HTML",
        reply_markup=menu_new_user(),
    )
    return RegState.ASK_STUDENT_ID


async def on_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    context.user_data.pop(UD_TEMP_STUDENT_ID, None)
    context.user_data.pop(UD_REG_NEEDS_ECLASS, None)
    await query.edit_message_text("🔙 Back. Use /start when you’re ready.", parse_mode="HTML")
    return ConversationHandler.END


def build_registration_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("start", start_cmd)],
        states={
            RegState.ASK_STUDENT_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_student_id_input),
            ],
            RegState.CONFIRM_STUDENT_ID: [
                CallbackQueryHandler(on_confirm_callback, pattern=f"^{CB_CONFIRM_ID}$"),
                CallbackQueryHandler(on_change_callback, pattern=f"^{CB_CHANGE_ID}$"),
                CallbackQueryHandler(on_back_callback, pattern=f"^{CB_BACK}$"),
            ],
            RegState.ASK_ECLASS_PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_eclass_password_input),
            ],
        },
        fallbacks=[
            CommandHandler("start", start_cmd),
            MessageHandler(filters.Regex(f"^{BTN_BACK}$"), back_from_new_user),
        ],
        allow_reentry=True,
    )
