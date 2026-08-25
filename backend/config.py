"""Configuration management for SyncAgent.

Loads environment variables from .env file and provides validated settings.
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Setup logging first before anything else
try:
    from backend.logging_config import setup_logging
    setup_logging()
except Exception:
    # Fallback if logging setup fails
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class Settings:
    """Application configuration settings.
    
    Loads configuration from environment variables with sensible defaults.
    Validates that required variables are present.
    """

    GOOGLE_CLOUD_PROJECT: str | None = os.getenv("GOOGLE_CLOUD_PROJECT")
    GOOGLE_CLOUD_LOCATION: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    CLICKHOUSE_HOST: str | None = os.getenv("CLICKHOUSE_HOST")
    CLICKHOUSE_USER: str | None = os.getenv("CLICKHOUSE_USER")
    CLICKHOUSE_PASSWORD: str | None = os.getenv("CLICKHOUSE_PASSWORD")

    @classmethod
    def validate(cls) -> None:
        """Validate that all required environment variables are set.
        
        Raises:
            ValueError: If any required configuration is missing.
        """
        required = {
            "GOOGLE_CLOUD_PROJECT": cls.GOOGLE_CLOUD_PROJECT,
            "CLICKHOUSE_HOST": cls.CLICKHOUSE_HOST,
            "CLICKHOUSE_USER": cls.CLICKHOUSE_USER,
            "CLICKHOUSE_PASSWORD": cls.CLICKHOUSE_PASSWORD,
        }
        
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                f"Check your .env file or set these variables."
            )
        
        logger.info("Configuration validated successfully")


settings = Settings()