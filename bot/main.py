import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from telegram.request import HTTPXRequest

from bot.config import get_settings
from bot.handlers.start import build_registration_conversation
from bot.handlers.eclass import build_eclass_conversation
from bot.handlers.common import build_menu_handlers
from bot.keyboards import CB_START_AGAIN
from bot import texts

logger = logging.getLogger("bot")


async def help_cmd(update, context):
    await update.effective_chat.send_message(texts.help_text(), parse_mode="HTML")


async def about_cmd(update, context):
    await update.effective_chat.send_message(texts.about_text(), parse_mode="HTML")


async def global_error_handler(update, context):
    import logging
    logging.exception("Unhandled exception:", exc_info=context.error)

def main():
    settings = get_settings()

    app = ApplicationBuilder().token(settings.bot_token).build()
    app.bot_data["settings"] = settings

    # GROUP 0 → start registration only
    # Conversations FIRST
    app.add_handler(build_registration_conversation(), group=0)
    app.add_handler(build_eclass_conversation(), group=1)

    # Commands
    app.add_handler(CommandHandler("help", help_cmd), group=2)
    app.add_handler(CommandHandler("about", about_cmd), group=2)

    # Menu handlers LAST
    for h in build_menu_handlers():
        app.add_handler(h, group=10)


    app.add_error_handler(global_error_handler)

    app.run_polling(drop_pending_updates=True)
if __name__ == "__main__":
    main()
