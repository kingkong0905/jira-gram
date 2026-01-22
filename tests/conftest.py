"""Test fixtures and utilities."""

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, Mock

import pytest

if TYPE_CHECKING:
    from telegram import CallbackQuery, Chat, Message, Update, User  # noqa: F401
    from telegram.ext import ContextTypes  # noqa: F401


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    settings = Mock()
    settings.telegram_bot_token = "test_token"
    settings.webhook_url = "https://test.com"
    settings.webhook_path = "/webhook"
    settings.jira_url = "https://test.atlassian.net"
    settings.jira_email = "test@example.com"
    settings.jira_api_token = "test_api_token"
    settings.host = "0.0.0.0"
    settings.port = 8000
    settings.allowed_users = ""
    settings.allowed_user_ids = []
    return settings


@pytest.fixture
def mock_jira_client():
    """Mock Jira client for testing."""
    client = Mock()
    client.get_issue.return_value = {
        "key": "PROJ-123",
        "summary": "Test Issue",
        "description": "Test description",
        "status": "To Do",
        "assignee": "Test User",
        "reporter": "Reporter User",
        "priority": "High",
        "created": "2024-01-01T00:00:00.000+0000",
        "updated": "2024-01-02T00:00:00.000+0000",
        "url": "https://test.atlassian.net/browse/PROJ-123",
    }
    client.add_comment.return_value = True
    client.search_issues.return_value = [
        {
            "key": "PROJ-123",
            "summary": "Test Issue 1",
            "status": "To Do",
            "assignee": "User 1",
            "url": "https://test.atlassian.net/browse/PROJ-123",
        },
        {
            "key": "PROJ-124",
            "summary": "Test Issue 2",
            "status": "In Progress",
            "assignee": "User 2",
            "url": "https://test.atlassian.net/browse/PROJ-124",
        },
    ]
    client.get_issue_comments.return_value = [
        {
            "id": "10000",
            "author": "Test User",
            "author_account_id": "account-123",
            "body": "Test comment",
            "created": "2024-01-01T00:00:00.000+0000",
        }
    ]
    client.reply_to_comment.return_value = True
    client.update_issue.return_value = True
    return client


@pytest.fixture
def mock_update():
    """Create a mock Telegram Update object."""
    update = Mock()
    user = Mock()
    user.id = 123456789
    user.first_name = "Test"
    user.username = "testuser"
    chat = Mock()
    chat.id = 123456789
    message = Mock()
    message.reply_text = AsyncMock()
    message.chat = chat
    update.effective_user = user
    update.message = message
    return update


@pytest.fixture
def mock_callback_query_update():
    """Create a mock Telegram Update with CallbackQuery."""
    update = Mock()
    user = Mock()
    user.id = 123456789
    user.first_name = "Test"
    user.username = "testuser"
    callback_query = Mock()
    callback_query.answer = AsyncMock()
    callback_query.edit_message_text = AsyncMock()
    callback_query.data = "comments_PROJ-123"
    update.effective_user = user
    update.callback_query = callback_query
    return update


@pytest.fixture
def mock_context():
    """Create a mock Telegram context."""
    context = Mock()
    context.args = []
    context.error = None
    return context


@pytest.fixture
def sample_jira_issue():
    """Sample Jira issue data."""
    return {
        "key": "PROJ-123",
        "summary": "Test Issue",
        "description": "This is a test issue description",
        "status": "To Do",
        "assignee": "John Doe",
        "reporter": "Jane Smith",
        "priority": "High",
        "created": "2024-01-01T00:00:00.000+0000",
        "updated": "2024-01-02T00:00:00.000+0000",
        "url": "https://test.atlassian.net/browse/PROJ-123",
    }


@pytest.fixture
def sample_jira_comments():
    """Sample Jira comments data."""
    return [
        {
            "id": "10000",
            "author": "John Doe",
            "author_account_id": "account-123",
            "body": "First comment",
            "created": "2024-01-01T00:00:00.000+0000",
        },
        {
            "id": "10001",
            "author": "Jane Smith",
            "author_account_id": "account-456",
            "body": "Second comment",
            "created": "2024-01-02T00:00:00.000+0000",
        },
    ]
