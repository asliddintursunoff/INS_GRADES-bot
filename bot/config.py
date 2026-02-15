import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    bot_token: str
    base_url: str
    http_timeout_seconds: float
    tz: str

def get_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    if not bot_token:
        raise RuntimeError("BOT_TOKEN is missing")

    base_url = os.getenv("BASE_URL", "https://ins-grades-backend-production.up.railway.app").strip().rstrip("/")
    timeout_s = float(os.getenv("HTTP_TIMEOUT_SECONDS", "25"))
    tz = os.getenv("TZ", "Asia/Tashkent")

    return Settings(
        bot_token=bot_token,
        base_url=base_url,
        http_timeout_seconds=timeout_s,
        tz=tz,
    )
