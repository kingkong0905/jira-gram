"""Tests for Jira client."""

from unittest.mock import Mock, patch

import pytest

from jira_gram.jira.client import JiraClient


class TestJiraClient:
    """Test JiraClient class."""

    @pytest.fixture
    def jira_client(self):
        """Create a JiraClient instance for testing."""
        with patch("jira_gram.jira.client.JIRA"):
            client = JiraClient(
                url="https://test.atlassian.net",
                email="test@example.com",
                api_token="test_token",
            )
            return client

    def test_init(self, jira_client):
        """Test JiraClient initialization."""
        assert jira_client.url == "https://test.atlassian.net"
        assert jira_client.email == "test@example.com"

    @patch("jira_gram.jira.client.JIRA")
    def test_get_issue_success(self, mock_jira_class, jira_client):
        """Test successful get_issue."""
        # Mock the issue object
        mock_issue = Mock()
        mock_issue.key = "PROJ-123"
        mock_issue.fields.summary = "Test Issue"
        mock_issue.fields.description = "Test description"
        mock_issue.fields.status.name = "To Do"
        mock_issue.fields.assignee.displayName = "Test User"
        mock_issue.fields.reporter.displayName = "Reporter"
        mock_issue.fields.priority.name = "High"
        mock_issue.fields.created = "2024-01-01T00:00:00.000+0000"
        mock_issue.fields.updated = "2024-01-02T00:00:00.000+0000"

        jira_client.jira.issue.return_value = mock_issue

        result = jira_client.get_issue("PROJ-123")

        assert result is not None
        assert result["key"] == "PROJ-123"
        assert result["summary"] == "Test Issue"
        assert result["status"] == "To Do"
        assert result["assignee"] == "Test User"

    @patch("jira_gram.jira.client.JIRA")
    def test_get_issue_not_found(self, mock_jira_class, jira_client):
        """Test get_issue when issue not found."""
        jira_client.jira.issue.side_effect = Exception("Issue not found")

        result = jira_client.get_issue("PROJ-999")

        assert result is None

    @patch("jira_gram.jira.client.JIRA")
    def test_get_issue_no_assignee(self, mock_jira_class, jira_client):
        """Test get_issue when issue has no assignee."""
        mock_issue = Mock()
        mock_issue.key = "PROJ-123"
        mock_issue.fields.summary = "Test Issue"
        mock_issue.fields.description = "Test description"
        mock_issue.fields.status.name = "To Do"
        mock_issue.fields.assignee = None
        mock_issue.fields.reporter.displayName = "Reporter"
        mock_issue.fields.priority.name = "High"
        mock_issue.fields.created = "2024-01-01T00:00:00.000+0000"
        mock_issue.fields.updated = "2024-01-02T00:00:00.000+0000"

        jira_client.jira.issue.return_value = mock_issue

        result = jira_client.get_issue("PROJ-123")

        assert result["assignee"] == "Unassigned"

    @patch("jira_gram.jira.client.JIRA")
    def test_add_comment_success(self, mock_jira_class, jira_client):
        """Test successful add_comment."""
        jira_client.jira.add_comment.return_value = True

        result = jira_client.add_comment("PROJ-123", "Test comment")

        assert result is True
        jira_client.jira.add_comment.assert_called_once_with("PROJ-123", "Test comment")

    @patch("jira_gram.jira.client.JIRA")
    def test_add_comment_failure(self, mock_jira_class, jira_client):
        """Test add_comment failure."""
        jira_client.jira.add_comment.side_effect = Exception("Failed to add comment")

        result = jira_client.add_comment("PROJ-123", "Test comment")

        assert result is False

    @patch("jira_gram.jira.client.JIRA")
    def test_search_issues_success(self, mock_jira_class, jira_client):
        """Test successful search_issues."""
        mock_issue1 = Mock()
        mock_issue1.key = "PROJ-123"
        mock_issue1.fields.summary = "Issue 1"
        mock_issue1.fields.status.name = "To Do"
        mock_issue1.fields.assignee.displayName = "User 1"

        mock_issue2 = Mock()
        mock_issue2.key = "PROJ-124"
        mock_issue2.fields.summary = "Issue 2"
        mock_issue2.fields.status.name = "In Progress"
        mock_issue2.fields.assignee = None

        jira_client.jira.search_issues.return_value = [mock_issue1, mock_issue2]

        result = jira_client.search_issues("assignee = currentUser()")

        assert len(result) == 2
        assert result[0]["key"] == "PROJ-123"
        assert result[1]["key"] == "PROJ-124"
        assert result[1]["assignee"] == "Unassigned"

    @patch("jira_gram.jira.client.JIRA")
    def test_search_issues_failure(self, mock_jira_class, jira_client):
        """Test search_issues failure."""
        jira_client.jira.search_issues.side_effect = Exception("Search failed")

        result = jira_client.search_issues("invalid JQL")

        assert result == []

    @patch("jira_gram.jira.client.JIRA")
    def test_get_issue_comments_success(self, mock_jira_class, jira_client):
        """Test successful get_issue_comments."""
        mock_comment1 = Mock()
        mock_comment1.author.displayName = "User 1"
        mock_comment1.body = "Comment 1"
        mock_comment1.created = "2024-01-01T00:00:00.000+0000"

        mock_comment2 = Mock()
        mock_comment2.author.displayName = "User 2"
        mock_comment2.body = "Comment 2"
        mock_comment2.created = "2024-01-02T00:00:00.000+0000"

        mock_issue = Mock()
        mock_issue.fields.comment.comments = [mock_comment1, mock_comment2]

        jira_client.jira.issue.return_value = mock_issue

        result = jira_client.get_issue_comments("PROJ-123")

        assert len(result) == 2
        assert result[0]["author"] == "User 1"
        assert result[1]["body"] == "Comment 2"

    @patch("jira_gram.jira.client.JIRA")
    def test_get_issue_comments_failure(self, mock_jira_class, jira_client):
        """Test get_issue_comments failure."""
        jira_client.jira.issue.side_effect = Exception("Failed to get comments")

        result = jira_client.get_issue_comments("PROJ-123")

        assert result == []

    @patch("jira_gram.jira.client.JIRA")
    def test_update_issue_success(self, mock_jira_class, jira_client):
        """Test successful update_issue."""
        mock_issue = Mock()
        mock_issue.update.return_value = True
        jira_client.jira.issue.return_value = mock_issue

        result = jira_client.update_issue("PROJ-123", {"summary": "Updated"})

        assert result is True
        mock_issue.update.assert_called_once_with(fields={"summary": "Updated"})

    @patch("jira_gram.jira.client.JIRA")
    def test_update_issue_failure(self, mock_jira_class, jira_client):
        """Test update_issue failure."""
        jira_client.jira.issue.side_effect = Exception("Update failed")

        result = jira_client.update_issue("PROJ-123", {"summary": "Updated"})

        assert result is False
