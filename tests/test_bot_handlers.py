"""Tests for bot handlers."""

from unittest.mock import patch

import pytest

from jira_gram.bot import handlers


class TestStartCommand:
    """Test start command handler."""

    @pytest.mark.asyncio
    @patch("jira_gram.bot.handlers.is_authorized")
    async def test_start_command_authorized(self, mock_is_authorized, mock_update, mock_context):
        """Test start command with authorized user."""
        mock_is_authorized.return_value = True

        await handlers.start_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Welcome to Jira Telegram Bot" in call_args

    @pytest.mark.asyncio
    @patch("jira_gram.bot.handlers.is_authorized")
    async def test_start_command_unauthorized(self, mock_is_authorized, mock_update, mock_context):
        """Test start command with unauthorized user."""
        mock_is_authorized.return_value = False

        await handlers.start_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once_with(
            "Sorry, you are not authorized to use this bot."
        )


class TestViewCommand:
    """Test view command handler."""

    @pytest.mark.asyncio
    @patch("jira_gram.bot.handlers.is_authorized")
    async def test_view_command_no_args(self, mock_is_authorized, mock_update, mock_context):
        """Test view command without arguments."""
        mock_is_authorized.return_value = True
        mock_context.args = []

        await handlers.view_command(mock_update, mock_context)

        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Please provide an issue key" in call_args

    @pytest.mark.asyncio
    @patch("jira_gram.bot.handlers.get_jira_client")
    @patch("jira_gram.bot.handlers.is_authorized")
    async def test_view_command_invalid_format(
        self, mock_is_authorized, mock_get_client, mock_update, mock_context
    ):
        """Test view command with invalid issue key format."""
        mock_is_authorized.return_value = True
        mock_context.args = ["invalid"]

        await handlers.view_command(mock_update, mock_context)

        # Should be called twice: once for fetching message, once for error
        assert mock_update.message.reply_text.call_count >= 1
        last_call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Invalid issue key format" in last_call_args

    @pytest.mark.asyncio
    @patch("jira_gram.bot.handlers.get_jira_client")
    @patch("jira_gram.bot.handlers.is_authorized")
    async def test_view_command_issue_not_found(
        self,
        mock_is_authorized,
        mock_get_client,
        mock_update,
        mock_context,
        mock_jira_client,
    ):
        """Test view command when issue is not found."""
        mock_is_authorized.return_value = True
        mock_context.args = ["PROJ-123"]
        mock_jira_client.get_issue.return_value = None
        mock_get_client.return_value = mock_jira_client

        await handlers.view_command(mock_update, mock_context)

        # Check that error message was sent
        calls = mock_update.message.reply_text.call_args_list
        assert any("Could not find issue" in str(call) for call in calls)

    @pytest.mark.asyncio
    @patch("jira_gram.bot.handlers.get_jira_client")
    @patch("jira_gram.bot.handlers.is_authorized")
    async def test_view_command_success(
        self,
        mock_is_authorized,
        mock_get_client,
        mock_update,
        mock_context,
        mock_jira_client,
        sample_jira_issue,
    ):
        """Test successful view command."""
        mock_is_authorized.return_value = True
        mock_context.args = ["PROJ-123"]
        mock_jira_client.get_issue.return_value = sample_jira_issue
        mock_get_client.return_value = mock_jira_client

        await handlers.view_command(mock_update, mock_context)

        # Check that issue details were sent
        calls = mock_update.message.reply_text.call_args_list
        assert len(calls) >= 2  # Fetching message + issue details
        last_call = calls[-1]
        assert "PROJ-123" in str(last_call)


class TestCommentCommand:
    """Test comment command handler."""

    @pytest.mark.asyncio
    @patch("jira_gram.bot.handlers.is_authorized")
    async def test_comment_command_no_args(self, mock_is_authorized, mock_update, mock_context):
        """Test comment command without arguments."""
        mock_is_authorized.return_value = True
        mock_context.args = []

        await handlers.comment_command(mock_update, mock_context)

        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Please provide an issue key and comment" in call_args

    @pytest.mark.asyncio
    @patch("jira_gram.bot.handlers.is_authorized")
    async def test_comment_command_only_issue_key(
        self, mock_is_authorized, mock_update, mock_context
    ):
        """Test comment command with only issue key."""
        mock_is_authorized.return_value = True
        mock_context.args = ["PROJ-123"]

        await handlers.comment_command(mock_update, mock_context)

        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Please provide an issue key and comment" in call_args

    @pytest.mark.asyncio
    @patch("jira_gram.bot.handlers.get_jira_client")
    @patch("jira_gram.bot.handlers.is_authorized")
    async def test_comment_command_success(
        self,
        mock_is_authorized,
        mock_get_client,
        mock_update,
        mock_context,
        mock_jira_client,
    ):
        """Test successful comment command."""
        mock_is_authorized.return_value = True
        mock_context.args = ["PROJ-123", "Test", "comment"]
        mock_jira_client.add_comment.return_value = True
        mock_get_client.return_value = mock_jira_client

        await handlers.comment_command(mock_update, mock_context)

        # Check that success message was sent
        calls = mock_update.message.reply_text.call_args_list
        assert any("successfully" in str(call).lower() for call in calls)

    @pytest.mark.asyncio
    @patch("jira_gram.bot.handlers.get_jira_client")
    @patch("jira_gram.bot.handlers.is_authorized")
    async def test_comment_command_failure(
        self,
        mock_is_authorized,
        mock_get_client,
        mock_update,
        mock_context,
        mock_jira_client,
    ):
        """Test comment command when adding comment fails."""
        mock_is_authorized.return_value = True
        mock_context.args = ["PROJ-123", "Test", "comment"]
        mock_jira_client.add_comment.return_value = False
        mock_get_client.return_value = mock_jira_client

        await handlers.comment_command(mock_update, mock_context)

        # Check that failure message was sent
        calls = mock_update.message.reply_text.call_args_list
        assert any("Failed" in str(call) for call in calls)


class TestSearchCommand:
    """Test search command handler."""

    @pytest.mark.asyncio
    @patch("jira_gram.bot.handlers.is_authorized")
    async def test_search_command_no_args(self, mock_is_authorized, mock_update, mock_context):
        """Test search command without arguments."""
        mock_is_authorized.return_value = True
        mock_context.args = []

        await handlers.search_command(mock_update, mock_context)

        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Please provide a JQL query" in call_args

    @pytest.mark.asyncio
    @patch("jira_gram.bot.handlers.get_jira_client")
    @patch("jira_gram.bot.handlers.is_authorized")
    async def test_search_command_no_results(
        self,
        mock_is_authorized,
        mock_get_client,
        mock_update,
        mock_context,
        mock_jira_client,
    ):
        """Test search command with no results."""
        mock_is_authorized.return_value = True
        mock_context.args = ["assignee", "=", "currentUser()"]
        mock_jira_client.search_issues.return_value = []
        mock_get_client.return_value = mock_jira_client

        await handlers.search_command(mock_update, mock_context)

        calls = mock_update.message.reply_text.call_args_list
        assert any("No issues found" in str(call) for call in calls)

    @pytest.mark.asyncio
    @patch("jira_gram.bot.handlers.get_jira_client")
    @patch("jira_gram.bot.handlers.is_authorized")
    async def test_search_command_success(
        self,
        mock_is_authorized,
        mock_get_client,
        mock_update,
        mock_context,
        mock_jira_client,
    ):
        """Test successful search command."""
        mock_is_authorized.return_value = True
        mock_context.args = ["assignee", "=", "currentUser()"]
        mock_get_client.return_value = mock_jira_client

        await handlers.search_command(mock_update, mock_context)

        calls = mock_update.message.reply_text.call_args_list
        # Should show search results
        assert any("Search Results" in str(call) for call in calls)


class TestButtonCallback:
    """Test button callback handler."""

    @pytest.mark.asyncio
    @patch("jira_gram.bot.handlers.get_jira_client")
    @patch("jira_gram.bot.handlers.is_authorized")
    async def test_button_callback_comments(
        self,
        mock_is_authorized,
        mock_get_client,
        mock_callback_query_update,
        mock_context,
        mock_jira_client,
        sample_jira_comments,
    ):
        """Test button callback for viewing comments."""
        mock_is_authorized.return_value = True
        mock_callback_query_update.callback_query.data = "comments_PROJ-123"
        mock_jira_client.get_issue_comments.return_value = sample_jira_comments
        mock_get_client.return_value = mock_jira_client

        await handlers.button_callback(mock_callback_query_update, mock_context)

        mock_callback_query_update.callback_query.answer.assert_called_once()
        mock_callback_query_update.callback_query.edit_message_text.assert_called_once()

        call_args = mock_callback_query_update.callback_query.edit_message_text.call_args[0][0]
        assert "Comments for PROJ-123" in call_args

    @pytest.mark.asyncio
    @patch("jira_gram.bot.handlers.is_authorized")
    async def test_button_callback_add_comment(
        self, mock_is_authorized, mock_callback_query_update, mock_context
    ):
        """Test button callback for add comment prompt."""
        mock_is_authorized.return_value = True
        mock_callback_query_update.callback_query.data = "comment_PROJ-123"

        await handlers.button_callback(mock_callback_query_update, mock_context)

        mock_callback_query_update.callback_query.answer.assert_called_once()
        call_args = mock_callback_query_update.callback_query.edit_message_text.call_args[0][0]
        assert "/comment PROJ-123" in call_args


class TestErrorHandler:
    """Test error handler."""

    @pytest.mark.asyncio
    async def test_error_handler(self, mock_update, mock_context):
        """Test error handler logs errors."""
        mock_context.error = Exception("Test error")

        # Should not raise exception
        await handlers.error_handler(mock_update, mock_context)
