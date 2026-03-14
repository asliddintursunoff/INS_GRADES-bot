import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN
from bot.api_client import APIClient
from bot.handlers import start, timetable, assignments, payment

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    api_client = APIClient()

    # Register handlers
    dp.include_router(start.router)
    dp.include_router(timetable.router)
    dp.include_router(assignments.router)
    dp.include_router(payment.router)

    try:
        # Start polling
        await dp.start_polling(bot, api_client=api_client)
    finally:
        await api_client.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
