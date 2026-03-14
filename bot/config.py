import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")
if not API_BASE_URL:
    raise ValueError("API_BASE_URL is not set in environment variables")
