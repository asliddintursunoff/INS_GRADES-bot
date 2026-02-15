from __future__ import annotations

import httpx
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.config import Settings
from bot.api_client import BackendClient, ApiError
from bot import texts
from bot.keyboards import (
    BTN_ECLASS,
    BTN_TIMETABLE,
    BTN_ATTENDANCE,
    BTN_ASSIGNMENTS,
    BTN_BACK,
    remove_keyboard,
    back_only_kb,
    menu_for_user_type,
)
from bot.states import EclassState
from bot.utils import is_valid_student_id, normalize_student_id
from bot.services.user_service import determine_user_type


UD_TEMP_STUDENT_ID = "temp_student_id"
FLOW_FLAG = "in_eclass_flow"

MENU_TEXTS = {
    BTN_TIMETABLE,
    BTN_ATTENDANCE,
    BTN_ASSIGNMENTS,
    BTN_ECLASS,
}


# =====================================================
# ENTRY
# =====================================================
async def eclass_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    settings: Settings = context.bot_data["settings"]
    telegram_id = str(update.effective_user.id)

    # 🔥 mark user inside flow (prevents help spam)
    context.user_data[FLOW_FLAG] = True
    context.user_data.pop(UD_TEMP_STUDENT_ID, None)

    user_type = await determine_user_type(settings, telegram_id)

    if user_type != "half_user":
        context.user_data.pop(FLOW_FLAG, None)

        await update.effective_chat.send_message(
            "✅ E-class is already connected.",
            parse_mode="HTML",
            reply_markup=menu_for_user_type(user_type),
        )
        return ConversationHandler.END

    # try to get student_id from backend
    student_id = None
    try:
        async with BackendClient(settings.base_url, settings.http_timeout_seconds) as api:
            info = await api.get_user_info(telegram_id)
            if info:
                student_id = info.get("student_id")
    except Exception:
        student_id = None

    # if no student id → ask for it
    if not student_id:
        await update.effective_chat.send_message(
            "🆔 Please enter your <b>Student ID</b> (U1234567).",
            parse_mode="HTML",
            reply_markup=back_only_kb(),
        )
        return EclassState.ASK_PASSWORD

    context.user_data[UD_TEMP_STUDENT_ID] = student_id

    await update.effective_chat.send_message(
        texts.ask_password(student_id),
        parse_mode="HTML",
        reply_markup=back_only_kb(),
    )

    return EclassState.ASK_PASSWORD


# =====================================================
# PASSWORD INPUT
# =====================================================
async def eclass_password_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    settings: Settings = context.bot_data["settings"]
    telegram_id = str(update.effective_user.id)
    text = (update.message.text or "").strip()

    # ==============================
    # BACK BUTTON
    # ==============================
    if text == BTN_BACK:
        context.user_data.pop(UD_TEMP_STUDENT_ID, None)
        context.user_data.pop(FLOW_FLAG, None)

        await update.effective_chat.send_message(
            "❌ E-class connection cancelled.\n\nUse /start to open the menu.",
            parse_mode="HTML",
            reply_markup=remove_keyboard(),
        )
        return ConversationHandler.END

    # ==============================
    # MENU BUTTON PRESSED INSIDE FLOW
    # ==============================
    if text in MENU_TEXTS:
        await update.effective_chat.send_message(
            "🔐 Please enter your E-class password first.\n\n⬅️ Or tap Back to cancel.",
            parse_mode="HTML",
            reply_markup=back_only_kb(),
        )
        return EclassState.ASK_PASSWORD

    student_id = context.user_data.get(UD_TEMP_STUDENT_ID)

    # ==============================
    # FIRST MESSAGE = STUDENT ID
    # ==============================
    if not student_id:
        if not is_valid_student_id(text):
            await update.effective_chat.send_message(
                texts.invalid_student_id(),
                parse_mode="HTML",
                reply_markup=back_only_kb(),
            )
            return EclassState.ASK_PASSWORD

        student_id = normalize_student_id(text)
        context.user_data[UD_TEMP_STUDENT_ID] = student_id

        await update.effective_chat.send_message(
            texts.ask_password(student_id),
            parse_mode="HTML",
            reply_markup=back_only_kb(),
        )
        return EclassState.ASK_PASSWORD

    # ==============================
    # PASSWORD PROCESSING
    # ==============================
    password = text

    if not password:
        await update.effective_chat.send_message(
            "❌ Password can’t be empty. Try again.",
            parse_mode="HTML",
            reply_markup=back_only_kb(),
        )
        return EclassState.ASK_PASSWORD

    wait_msg = await update.effective_chat.send_message(
        texts.connecting_eclass(),
        parse_mode="HTML",
        reply_markup=remove_keyboard(),
    )

    try:
        async with BackendClient(settings.base_url, settings.http_timeout_seconds) as api:
            resp = await api.register_eclass(
                telegram_id=telegram_id,
                student_id=student_id,
                password=password,
            )

        # 🔥 Return EXACT backend detail
        detail = str((resp or {}).get("detail") or "")
        print(detail)
        try:
            await wait_msg.edit_text(detail, parse_mode="HTML")
        except Exception:
            await update.effective_chat.send_message(detail, parse_mode="HTML")


        # remove buttons while backend background task runs
       

        context.user_data.pop(UD_TEMP_STUDENT_ID, None)
        context.user_data.pop(FLOW_FLAG, None)

        return ConversationHandler.END

    # ==============================
    # WRONG PASSWORD
    # ==============================
    except ApiError as e:
        if e.status_code == 403:
            await update.effective_chat.send_message(
                "❌ Password is incorrect. Please try again.\n\n⬅️ Or tap Back to cancel.",
                parse_mode="HTML",
                reply_markup=back_only_kb(),
            )
            return EclassState.ASK_PASSWORD

        context.user_data.pop(FLOW_FLAG, None)

        await update.effective_chat.send_message(
            f"⚠️ {e.detail}",
            parse_mode="HTML",
            reply_markup=remove_keyboard(),
        )
        return ConversationHandler.END

    # ==============================
    # NETWORK ERROR
    # ==============================
    except (httpx.TimeoutException, httpx.ConnectTimeout, httpx.ReadTimeout):
        # ✅ very common: backend started job but response didn't arrive before timeout
        # Treat as accepted and tell user to wait
        await update.effective_chat.send_message(
            "⏳ Request sent. Backend is setting up your data.\n"
            "It may take up to 15 minutes if many users.\n\n"
            "✅ Please wait for the bot notification, then click /start.",
            parse_mode="HTML",
            reply_markup=remove_keyboard(),
        )

        context.user_data.pop(UD_TEMP_STUDENT_ID, None)
        context.user_data.pop(FLOW_FLAG, None)
        context.user_data["setup_waiting"] = True   # 🔥 used to block menu
        return ConversationHandler.END

    except Exception as e:
        context.user_data.pop(FLOW_FLAG, None)
        print(str(e))
        await update.effective_chat.send_message(
            "⚠️ Unexpected error. Please try again later.",
            parse_mode="HTML",
            reply_markup=remove_keyboard(),
        )
        return ConversationHandler.END


# =====================================================
# CONVERSATION BUILDER
# =====================================================
def build_eclass_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex(f"^{BTN_ECLASS}$"), eclass_entry)
        ],
        states={
            EclassState.ASK_PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, eclass_password_input),
            ],
        },
        fallbacks=[],
        allow_reentry=True,
        per_message=False,
        per_chat=True,
        per_user=True,
        block=True,
    )
