import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

class Settings:
    GOOGLE_CLOUD_PROJECT: str | None = os.getenv("GOOGLE_CLOUD_PROJECT")
    GOOGLE_CLOUD_LOCATION: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    CLICKHOUSE_HOST: str | None = os.getenv("CLICKHOUSE_HOST")
    CLICKHOUSE_USER: str | None = os.getenv("CLICKHOUSE_USER")
    CLICKHOUSE_PASSWORD: str | None = os.getenv("CLICKHOUSE_PASSWORD")

settings = Settings()