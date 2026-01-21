"""Jira client module for interacting with Jira API."""

from jira import JIRA
from typing import Optional, Dict, List
import config


class JiraClient:
    """Client for interacting with Jira."""

    def __init__(self):
        """Initialize Jira client with credentials from config."""
        self.jira = JIRA(
            server=config.JIRA_URL,
            basic_auth=(config.JIRA_EMAIL, config.JIRA_API_TOKEN),
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
                "assignee": issue.fields.assignee.displayName
                if issue.fields.assignee
                else "Unassigned",
                "reporter": issue.fields.reporter.displayName,
                "priority": issue.fields.priority.name
                if issue.fields.priority
                else "None",
                "created": issue.fields.created,
                "updated": issue.fields.updated,
                "url": f"{config.JIRA_URL}/browse/{issue.key}",
            }
        except Exception as e:
            print(f"Error fetching issue {issue_key}: {e}")
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
            print(f"Error adding comment to {issue_key}: {e}")
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
                    "assignee": issue.fields.assignee.displayName
                    if issue.fields.assignee
                    else "Unassigned",
                    "url": f"{config.JIRA_URL}/browse/{issue.key}",
                }
                for issue in issues
            ]
        except Exception as e:
            print(f"Error searching issues: {e}")
            return []

    def get_issue_comments(self, issue_key: str) -> List[Dict]:
        """
        Get all comments for a Jira issue.

        Args:
            issue_key: Jira issue key

        Returns:
            List of comment dictionaries
        """
        try:
            issue = self.jira.issue(issue_key, fields="comment")
            comments = issue.fields.comment.comments
            return [
                {
                    "author": comment.author.displayName,
                    "body": comment.body,
                    "created": comment.created,
                }
                for comment in comments
            ]
        except Exception as e:
            print(f"Error fetching comments for {issue_key}: {e}")
            return []

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
            print(f"Error updating issue {issue_key}: {e}")
            return False
