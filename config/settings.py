from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str

    telegram_token: str
    telegram_chat_id: str

    database_path: Path

    log_level: str


settings = Settings(
    openai_api_key=os.getenv("OPENAI_API_KEY", ""),

    telegram_token=os.getenv("TELEGRAM_TOKEN", ""),
    telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),

    database_path=Path(
        os.getenv("DATABASE_PATH", "data/jobs.db")
    ),

    log_level=os.getenv("LOG_LEVEL", "INFO"),
)