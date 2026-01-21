"""Configuration module for the Jira-Telegram bot."""

from functools import lru_cache
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Telegram Bot Configuration
    telegram_bot_token: str
    webhook_url: Optional[str] = ""
    webhook_path: str = "/webhook"

    # Jira Configuration
    jira_url: str
    jira_email: str
    jira_api_token: str

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # Security: Optional list of allowed user IDs
    allowed_users: str = ""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    @field_validator("jira_url")
    @classmethod
    def validate_jira_url(cls, v: str) -> str:
        """Validate Jira URL format."""
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("JIRA_URL must start with http:// or https://")
        return v.rstrip("/")

    @property
    def allowed_user_ids(self) -> List[int]:
        """Parse allowed user IDs from comma-separated string."""
        if not self.allowed_users:
            return []
        return [int(uid.strip()) for uid in self.allowed_users.split(",") if uid.strip()]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def validate_config() -> bool:
    """
    Validate that all required configuration is present.

    Raises:
        ValidationError: If configuration is invalid

    Returns:
        True if valid
    """
    # This will raise ValidationError if any required fields are missing
    get_settings()
    return True
