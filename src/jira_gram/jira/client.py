"""Jira client module for interacting with Jira API."""

import logging
from typing import Dict, List, Optional, Union

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
            List of comment dictionaries with id, author, body, created, and accountId fields
        """
        try:
            issue = self.jira.issue(issue_key, fields="comment")
            comments = issue.fields.comment.comments
            return [
                {
                    "id": comment.id,
                    "author": comment.author.displayName,
                    "author_account_id": getattr(comment.author, "accountId", None),
                    "body": comment.body,
                    "created": comment.created,
                }
                for comment in comments
            ]
        except Exception as e:
            logger.error(f"Error fetching comments for {issue_key}: {e}")
            return []

    def reply_to_comment(
        self,
        issue_key: str,
        parent_comment_id: str,
        reply_text: str,
        mention_account_id: Optional[str] = None,
        mention_display_name: Optional[str] = None,
    ) -> bool:
        """
        Reply to a specific comment on a Jira issue using ADF format.

        Note: Jira doesn't have native "reply-to" API support, so we include
        a link to the original comment in the reply body using ADF format.

        Args:
            issue_key: Jira issue key
            parent_comment_id: ID of the parent comment to reply to
            reply_text: Reply text (plain text without mentions)
            mention_account_id: Optional account ID of the user to mention
            mention_display_name: Optional display name of the user to mention

        Returns:
            True if successful, False otherwise
        """
        # Build comment URL for linking to the original comment
        comment_url = (
            f"{self.url}/browse/{issue_key}?focusedCommentId={parent_comment_id}"
            f"&page=com.atlassian.jira.plugin.system.issuetabpanels:comment-tab"
            f"#comment-{parent_comment_id}"
        )

        # Strategy: Try multiple formats in order of preference
        # 1. ADF format with mention and link to original comment
        # 2. ADF format with link only (no mention)
        # 3. Plain text with mention (fallback)
        # 4. Plain comment (last resort)

        attempts: List[tuple[str, Union[Dict, str]]] = []

        # Build ADF content for the reply text
        # For simplicity, put the entire reply text in one text node
        # If reply contains newlines, we could split into multiple paragraphs
        reply_content = [{"type": "text", "text": reply_text}]

        # Attempt 1: ADF format with mention and link
        if mention_account_id and mention_display_name:
            adf_body_with_mention = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": "Replying to "},
                            {
                                "type": "text",
                                "text": f"comment #{parent_comment_id}",
                                "marks": [{"type": "link", "attrs": {"href": comment_url}}],
                            },
                            {"type": "text", "text": " and mentioning "},
                            {
                                "type": "mention",
                                "attrs": {
                                    "id": mention_account_id,
                                    "text": f"@{mention_display_name}",
                                },
                            },
                            {"type": "text", "text": ". "},
                        ]
                        + reply_content,
                    }
                ],
            }
            attempts.append(("ADF with mention and link", {"body": adf_body_with_mention}))

        # Attempt 2: ADF format with link only
        adf_body_with_link = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Replying to "},
                        {
                            "type": "text",
                            "text": f"comment #{parent_comment_id}",
                            "marks": [{"type": "link", "attrs": {"href": comment_url}}],
                        },
                        {"type": "text", "text": ". "},
                    ]
                    + reply_content,
                }
            ],
        }
        attempts.append(("ADF with link only", {"body": adf_body_with_link}))

        # Attempt 3: Plain text with mention (fallback)
        if mention_account_id:
            # Try the old format as fallback
            plain_text_with_mention = f"[~accountid:{{{mention_account_id}}}] {reply_text}"
            attempts.append(("plain text with mention", plain_text_with_mention))

        # Attempt 4: Plain comment (last resort)
        attempts.append(("plain comment", reply_text))

        for attempt_name, comment_body in attempts:
            try:
                logger.debug(
                    f"Attempting {attempt_name} - Issue: {issue_key}, "
                    f"Parent ID: {parent_comment_id}, Body type: {type(comment_body).__name__}"
                )
                if isinstance(comment_body, dict):
                    self.jira.add_comment(issue_key, comment_body)
                else:
                    self.jira.add_comment(issue_key, comment_body)
                logger.info(
                    f"Successfully added comment using {attempt_name} - "
                    f"Issue: {issue_key}, Comment ID: {parent_comment_id}"
                )
                return True
            except Exception as e:
                logger.debug(f"Failed {attempt_name} - Issue: {issue_key}, Error: {str(e)[:200]}")
                continue

        # All attempts failed
        logger.error(
            f"All comment attempts failed - Issue: {issue_key}, "
            f"Parent ID: {parent_comment_id}, Reply length: {len(reply_text)}",
            exc_info=True,
        )
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
