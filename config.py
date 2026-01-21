"""Configuration module for the Jira-Telegram bot."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")  # e.g., https://yourdomain.com/webhook
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")

# Jira Configuration
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Security: Optional list of allowed user IDs
ALLOWED_USERS = os.getenv("ALLOWED_USERS", "")
ALLOWED_USER_IDS = [int(uid.strip()) for uid in ALLOWED_USERS.split(",") if uid.strip()]


def validate_config():
    """Validate that all required configuration is present."""
    missing = []

    if not TELEGRAM_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not JIRA_URL:
        missing.append("JIRA_URL")
    if not JIRA_EMAIL:
        missing.append("JIRA_EMAIL")
    if not JIRA_API_TOKEN:
        missing.append("JIRA_API_TOKEN")

    if missing:
        raise ValueError(f"Missing required configuration: {', '.join(missing)}")

    return True
