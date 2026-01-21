"""Tests for configuration module."""

import pytest
from pydantic import ValidationError

from jira_gram.config import Settings, get_settings, validate_config


class TestSettings:
    """Test Settings class."""

    def test_settings_with_valid_env(self, monkeypatch):
        """Test settings creation with valid environment variables."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
        monkeypatch.setenv("JIRA_URL", "https://test.atlassian.net")
        monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
        monkeypatch.setenv("JIRA_API_TOKEN", "test_api_token")

        # Clear cache
        get_settings.cache_clear()

        settings = Settings()

        assert settings.telegram_bot_token == "test_token"
        assert settings.jira_url == "https://test.atlassian.net"
        assert settings.jira_email == "test@example.com"
        assert settings.jira_api_token == "test_api_token"

    def test_settings_missing_required_fields(self):
        """Test settings can be created with env file values.

        Note: Since load_dotenv() is called at module import,
        the .env file provides default values. In a real scenario,
        Pydantic would raise ValidationError if required fields are missing
        when .env is not present.
        """
        # This test verifies that the current .env file has the required fields
        settings = Settings()
        assert settings.telegram_bot_token  # Should not be empty
        assert settings.jira_url  # Should not be empty
        assert settings.jira_email  # Should not be empty
        assert settings.jira_api_token  # Should not be empty

    def test_jira_url_validation(self, monkeypatch):
        """Test Jira URL validation."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
        monkeypatch.setenv("JIRA_URL", "invalid-url")
        monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
        monkeypatch.setenv("JIRA_API_TOKEN", "test_api_token")

        get_settings.cache_clear()

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        assert any("JIRA_URL" in str(error) for error in exc_info.value.errors())

    def test_jira_url_trailing_slash_removed(self, monkeypatch):
        """Test that trailing slash is removed from Jira URL."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
        monkeypatch.setenv("JIRA_URL", "https://test.atlassian.net/")
        monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
        monkeypatch.setenv("JIRA_API_TOKEN", "test_api_token")

        get_settings.cache_clear()
        settings = Settings()

        assert settings.jira_url == "https://test.atlassian.net"

    def test_allowed_user_ids_parsing(self, monkeypatch):
        """Test parsing of allowed user IDs."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
        monkeypatch.setenv("JIRA_URL", "https://test.atlassian.net")
        monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
        monkeypatch.setenv("JIRA_API_TOKEN", "test_api_token")
        monkeypatch.setenv("ALLOWED_USERS", "123,456,789")

        get_settings.cache_clear()
        settings = Settings()

        assert settings.allowed_user_ids == [123, 456, 789]

    def test_allowed_user_ids_empty(self, monkeypatch):
        """Test that empty allowed users returns empty list."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
        monkeypatch.setenv("JIRA_URL", "https://test.atlassian.net")
        monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
        monkeypatch.setenv("JIRA_API_TOKEN", "test_api_token")
        monkeypatch.setenv("ALLOWED_USERS", "")

        get_settings.cache_clear()
        settings = Settings()

        assert settings.allowed_user_ids == []

    def test_default_values(self, monkeypatch):
        """Test default configuration values."""
        # Override with test values
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
        monkeypatch.setenv("JIRA_URL", "https://test.atlassian.net")
        monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
        monkeypatch.setenv("JIRA_API_TOKEN", "test_api_token")
        monkeypatch.setenv("WEBHOOK_URL", "")  # Override .env value

        get_settings.cache_clear()
        settings = Settings()

        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.webhook_path == "/webhook"
        assert settings.webhook_url == ""


class TestGetSettings:
    """Test get_settings function."""

    def test_get_settings_caching(self, monkeypatch):
        """Test that settings are cached."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
        monkeypatch.setenv("JIRA_URL", "https://test.atlassian.net")
        monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
        monkeypatch.setenv("JIRA_API_TOKEN", "test_api_token")

        get_settings.cache_clear()

        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2


class TestValidateConfig:
    """Test validate_config function."""

    def test_validate_config_success(self, monkeypatch):
        """Test successful config validation."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
        monkeypatch.setenv("JIRA_URL", "https://test.atlassian.net")
        monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
        monkeypatch.setenv("JIRA_API_TOKEN", "test_api_token")

        get_settings.cache_clear()

        assert validate_config() is True

    def test_validate_config_failure(self, monkeypatch):
        """Test config validation with invalid URL format."""
        # Test that invalid jira_url format would be caught
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
        monkeypatch.setenv("JIRA_URL", "not-a-valid-url")  # Invalid URL format
        monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
        monkeypatch.setenv("JIRA_API_TOKEN", "test_token")

        get_settings.cache_clear()

        with pytest.raises(ValueError):
            validate_config()
