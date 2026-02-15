from telegram import Chat
from bot.api_client import BackendClient
from bot.config import Settings


async def determine_user_type(settings: Settings, telegram_id: str) -> str:
    async with BackendClient(settings.base_url, settings.http_timeout_seconds) as api:
        try:
            return await api.get_user_type(telegram_id)
        except Exception:
            return "new_user"


async def safe_send_html(chat: Chat, text: str, reply_markup=None):
    """
    Prevent Telegram timeout by splitting long messages.
    """
    CHUNK = 3800

    if len(text) <= CHUNK:
        await chat.send_message(text, parse_mode="HTML", reply_markup=reply_markup)
        return

    parts = [text[i:i + CHUNK] for i in range(0, len(text), CHUNK)]

    for idx, part in enumerate(parts):
        rm = reply_markup if idx == len(parts) - 1 else None
        await chat.send_message(part, parse_mode="HTML", reply_markup=rm)
