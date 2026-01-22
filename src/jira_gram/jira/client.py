"""Jira client module for interacting with Jira API."""

import logging
from typing import Dict, List, Optional

from jira import JIRA

logger = logging.getLogger(__name__)


class JiraClient:
    """Client for interacting with Jira."""

    def __init__(self, url: str, email: str, api_token: str):
        """
        Initialize Jira client with credentials.

        Args:
            url: Jira instance URL
            email: Jira account email
            api_token: Jira API token
        """
        self.url = url
        self.email = email
        self.jira = JIRA(
            server=url,
            basic_auth=(email, api_token),
        )

    def get_issue(self, issue_key: str) -> Optional[Dict]:
        """
        Get details of a Jira issue.

        Args:
            issue_key: Jira issue key (e.g., 'PROJ-123')

        Returns:
            Dictionary with issue details or None if not found
        """
        try:
            issue = self.jira.issue(issue_key)
            return {
                "key": issue.key,
                "summary": issue.fields.summary,
                "description": issue.fields.description or "No description",
                "status": issue.fields.status.name,
                "assignee": (
                    issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned"
                ),
                "reporter": issue.fields.reporter.displayName,
                "priority": (issue.fields.priority.name if issue.fields.priority else "None"),
                "created": issue.fields.created,
                "updated": issue.fields.updated,
                "url": f"{self.url}/browse/{issue.key}",
            }
        except Exception as e:
            logger.error(f"Error fetching issue {issue_key}: {e}")
            return None

    def add_comment(self, issue_key: str, comment_text: str) -> bool:
        """
        Add a comment to a Jira issue.

        Args:
            issue_key: Jira issue key
            comment_text: Comment text to add

        Returns:
            True if successful, False otherwise
        """
        try:
            self.jira.add_comment(issue_key, comment_text)
            return True
        except Exception as e:
            logger.error(f"Error adding comment to {issue_key}: {e}")
            return False

    def search_issues(self, jql: str, max_results: int = 10) -> List[Dict]:
        """
        Search for Jira issues using JQL.

        Args:
            jql: JQL query string
            max_results: Maximum number of results to return

        Returns:
            List of issue dictionaries
        """
        try:
            issues = self.jira.search_issues(jql, maxResults=max_results)
            return [
                {
                    "key": issue.key,
                    "summary": issue.fields.summary,
                    "status": issue.fields.status.name,
                    "assignee": (
                        issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned"
                    ),
                    "url": f"{self.url}/browse/{issue.key}",
                }
                for issue in issues
            ]
        except Exception as e:
            logger.error(f"Error searching issues: {e}")
            return []

    def get_issue_comments(self, issue_key: str) -> List[Dict]:
        """
        Get all comments for a Jira issue.

        Args:
            issue_key: Jira issue key

        Returns:
            List of comment dictionaries with id, author, body, and created fields
        """
        try:
            issue = self.jira.issue(issue_key, fields="comment")
            comments = issue.fields.comment.comments
            return [
                {
                    "id": comment.id,
                    "author": comment.author.displayName,
                    "body": comment.body,
                    "created": comment.created,
                }
                for comment in comments
            ]
        except Exception as e:
            logger.error(f"Error fetching comments for {issue_key}: {e}")
            return []

    def reply_to_comment(self, issue_key: str, parent_comment_id: str, reply_text: str) -> bool:
        """
        Reply to a specific comment on a Jira issue.

        Args:
            issue_key: Jira issue key
            parent_comment_id: ID of the parent comment to reply to
            reply_text: Reply text

        Returns:
            True if successful, False otherwise
        """
        try:
            # Jira API v3 supports parent comments
            # Format: { "body": "reply text", "parent": { "id": "parent_comment_id" } }
            comment_data = {"body": reply_text, "parent": {"id": parent_comment_id}}
            self.jira.add_comment(issue_key, comment_data)
            return True
        except Exception as e:
            logger.error(f"Error replying to comment {parent_comment_id} on {issue_key}: {e}")
            # Fallback: if parent comment reply fails, add as regular comment with mention
            try:
                fallback_comment = f"Reply to comment:\n{reply_text}"
                self.jira.add_comment(issue_key, fallback_comment)
                return True
            except Exception as fallback_error:
                logger.error(f"Error adding fallback comment: {fallback_error}")
                return False

    def update_issue(self, issue_key: str, fields: Dict) -> bool:
        """
        Update a Jira issue.

        Args:
            issue_key: Jira issue key
            fields: Dictionary of fields to update

        Returns:
            True if successful, False otherwise
        """
        try:
            issue = self.jira.issue(issue_key)
            issue.update(fields=fields)
            return True
        except Exception as e:
            logger.error(f"Error updating issue {issue_key}: {e}")
            return False
