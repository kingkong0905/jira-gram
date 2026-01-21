"""Tests for bot authorization module."""

from unittest.mock import patch

from jira_gram.bot.auth import is_authorized


class TestIsAuthorized:
    """Test is_authorized function."""

    @patch("jira_gram.bot.auth.get_settings")
    def test_authorized_user_in_allowed_list(self, mock_get_settings, mock_settings):
        """Test that user in allowed list is authorized."""
        mock_settings.allowed_user_ids = [123, 456, 789]
        mock_get_settings.return_value = mock_settings

        assert is_authorized(123) is True
        assert is_authorized(456) is True

    @patch("jira_gram.bot.auth.get_settings")
    def test_unauthorized_user_not_in_allowed_list(self, mock_get_settings, mock_settings):
        """Test that user not in allowed list is unauthorized."""
        mock_settings.allowed_user_ids = [123, 456, 789]
        mock_get_settings.return_value = mock_settings

        assert is_authorized(999) is False

    @patch("jira_gram.bot.auth.get_settings")
    def test_all_users_authorized_when_no_restrictions(self, mock_get_settings, mock_settings):
        """Test that all users are authorized when allowed list is empty."""
        mock_settings.allowed_user_ids = []
        mock_get_settings.return_value = mock_settings

        assert is_authorized(123) is True
        assert is_authorized(456) is True
        assert is_authorized(999) is True
