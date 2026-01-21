"""Authorization utilities for the bot."""

from jira_gram.config import get_settings


def is_authorized(user_id: int) -> bool:
    """
    Check if user is authorized to use the bot.

    Args:
        user_id: Telegram user ID

    Returns:
        True if authorized, False otherwise
    """
    settings = get_settings()
    allowed_user_ids = settings.allowed_user_ids

    if not allowed_user_ids:
        return True  # If no restrictions, allow all users

    return user_id in allowed_user_ids
