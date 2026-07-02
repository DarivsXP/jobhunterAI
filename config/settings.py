from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_model: str
    openai_base_url: str
    telegram_token: str
    telegram_chat_id: str
    database_path: Path
    log_level: str


settings = Settings(
    openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
    openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip(),
    openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions").strip(),
    telegram_token=os.getenv("TELEGRAM_TOKEN", "").strip(),
    telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", "").strip(),
    database_path=Path(
        os.getenv("DATABASE_PATH", "data/jobs.db").strip()
    ),
    log_level=os.getenv("LOG_LEVEL", "INFO").strip(),
)
