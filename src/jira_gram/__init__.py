"""Jira-Telegram Bot Package."""

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "A Telegram bot for managing Jira issues with FastAPI"

from .config import Settings, get_settings

__all__ = ["Settings", "get_settings", "__version__"]
