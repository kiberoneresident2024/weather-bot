import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class Settings:
    def __init__(self) -> None:
        default_db_path = DATA_DIR / "bot.db"
        self.vk_token = os.getenv("VK_TOKEN", "")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.db_url = os.getenv(
            "DB_URL", f"sqlite+aiosqlite:///{default_db_path}"
        )
        self.api_timeout = int(os.getenv("API_TIMEOUT", "15"))


settings = Settings()
