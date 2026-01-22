"""Telegram bot handlers for Jira integration."""

import logging
import re
from typing import Dict

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from jira_gram.config import get_settings
from jira_gram.jira import JiraClient

from .auth import is_authorized

logger = logging.getLogger(__name__)

# Store pending replies: {user_id: {"issue_key": str, "comment_id": str}}
pending_replies: Dict[int, Dict[str, str]] = {}


def get_jira_client() -> JiraClient:
    """Get a Jira client instance."""
    settings = get_settings()
    return JiraClient(
        url=settings.jira_url,
        email=settings.jira_email,
        api_token=settings.jira_api_token,
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return

    welcome_text = """
Welcome to Jira Telegram Bot! 🤖

Available commands:
/start - Show this help message
/view <ISSUE-KEY> - View Jira ticket details
/comment <ISSUE-KEY> <comment> - Add comment to a ticket
/search <JQL> - Search for issues using JQL

Examples:
• `/view PROJ-123` - View details of PROJ-123
• `/comment PROJ-123 This is working now` - Add comment
• `/search assignee = currentUser() AND status = "In Progress"` - Search your in-progress issues
    """
    await update.message.reply_text(welcome_text)


async def view_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /view command to display Jira ticket details."""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return

    if not context.args:
        await update.message.reply_text("Please provide an issue key. Usage: /view PROJ-123")
        return

    issue_key = context.args[0].upper()

    # Validate issue key format
    if not re.match(r"^[A-Z]+-\d+$", issue_key):
        await update.message.reply_text("Invalid issue key format. Use format like: PROJ-123")
        return

    await update.message.reply_text(f"Fetching {issue_key}...")

    jira_client = get_jira_client()
    issue = jira_client.get_issue(issue_key)

    if not issue:
        await update.message.reply_text(
            f"Could not find issue {issue_key}. Please check the issue key."
        )
        return

    # Format issue details
    message = f"""
🎫 <b>{issue["key"]}</b>

<b>Summary:</b> {issue["summary"]}

<b>Status:</b> {issue["status"]}
<b>Priority:</b> {issue["priority"]}
<b>Assignee:</b> {issue["assignee"]}
<b>Reporter:</b> {issue["reporter"]}

<b>Description:</b>
{issue["description"][:500]}{"..." if len(issue["description"]) > 500 else ""}

<b>Created:</b> {issue["created"][:10]}
<b>Updated:</b> {issue["updated"][:10]}

<a href="{issue["url"]}">View in Jira</a>
    """

    # Add action buttons
    keyboard = [
        [
            InlineKeyboardButton("📝 Add Comment", callback_data=f"comment_{issue_key}"),
            InlineKeyboardButton("💬 View Comments", callback_data=f"comments_{issue_key}"),
        ],
        [InlineKeyboardButton("🔗 Open in Jira", url=issue["url"])],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(message, parse_mode=ParseMode.HTML, reply_markup=reply_markup)


async def comment_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /comment command to add a comment to a Jira ticket."""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "Please provide an issue key and comment. Usage: /comment PROJ-123 Your comment here"
        )
        return

    issue_key = context.args[0].upper()
    comment_text = " ".join(context.args[1:])

    # Validate issue key format
    if not re.match(r"^[A-Z]+-\d+$", issue_key):
        await update.message.reply_text("Invalid issue key format. Use format like: PROJ-123")
        return

    await update.message.reply_text(f"Adding comment to {issue_key}...")

    # Add comment with user attribution
    user_name = update.effective_user.first_name or update.effective_user.username
    full_comment = f"Comment from Telegram ({user_name}):\n{comment_text}"

    jira_client = get_jira_client()
    success = jira_client.add_comment(issue_key, full_comment)

    if success:
        await update.message.reply_text(f"✅ Comment added successfully to {issue_key}!")
    else:
        await update.message.reply_text(
            f"❌ Failed to add comment to {issue_key}. Please check the issue key."
        )


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /search command to search for Jira issues."""
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return

    if not context.args:
        await update.message.reply_text(
            "Please provide a JQL query. Usage: /search assignee = currentUser()"
        )
        return

    jql = " ".join(context.args)

    await update.message.reply_text(f"Searching with JQL: {jql}...")

    jira_client = get_jira_client()
    issues = jira_client.search_issues(jql, max_results=10)

    if not issues:
        await update.message.reply_text("No issues found matching your query.")
        return

    message = f"<b>Search Results ({len(issues)} issues):</b>\n\n"

    for issue in issues:
        message += f"🎫 <b>{issue['key']}</b> - {issue['summary']}\n"
        message += f"   Status: {issue['status']} | Assignee: {issue['assignee']}\n"
        message += f'   <a href="{issue["url"]}">View</a>\n\n'

    await update.message.reply_text(message, parse_mode=ParseMode.HTML)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()

    if not is_authorized(update.effective_user.id):
        await query.edit_message_text("Sorry, you are not authorized to use this bot.")
        return

    data = query.data

    if data.startswith("comments_"):
        issue_key = data.replace("comments_", "")
        jira_client = get_jira_client()
        comments = jira_client.get_issue_comments(issue_key)

        if not comments:
            await query.edit_message_text(f"No comments found for {issue_key}.")
            return

        # Sort comments by created date (latest first)
        comments = sorted(comments, key=lambda x: x["created"], reverse=True)

        message = f"<b>💬 Comments for {issue_key} ({len(comments)} total):</b>\n\n"

        # Create keyboard with reply buttons for each comment
        keyboard = []

        for i, comment in enumerate(comments, 1):
            message += f"<b>{i}. {comment['author']}</b> ({comment['created'][:10]})\n"
            comment_body = comment["body"][:200]
            is_truncated = len(comment["body"]) > 200
            message += f"{comment_body}{'...' if is_truncated else ''}\n\n"

            # Create buttons for each comment
            comment_buttons = [
                InlineKeyboardButton(
                    f"↩️ Reply to comment {i}",
                    callback_data=f"reply_{issue_key}|{comment['id']}",
                )
            ]

            # Add "View Full" button if comment is truncated
            if is_truncated:
                comment_buttons.append(
                    InlineKeyboardButton(
                        "📄 View Full",
                        callback_data=f"view_comment_{issue_key}|{comment['id']}",
                    )
                )

            keyboard.append(comment_buttons)

        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f"view_{issue_key}")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

    elif data.startswith("comment_"):
        issue_key = data.replace("comment_", "")
        await query.edit_message_text(
            f"To add a comment to {issue_key}, use:\n\n"
            f"`/comment {issue_key} Your comment here`",
            parse_mode=ParseMode.MARKDOWN,
        )

    elif data.startswith("reply_"):
        # Format: reply_ISSUE-KEY|COMMENT_ID (using | as delimiter to avoid conflicts)
        data_parts = data.replace("reply_", "")
        if "|" in data_parts:
            parts = data_parts.split("|", 1)
            if len(parts) == 2:
                issue_key = parts[0]
                comment_id = parts[1]
                user_id = update.effective_user.id
                username = update.effective_user.username or update.effective_user.first_name

                logger.info(
                    f"Reply initiated - User: {user_id} ({username}), "
                    f"Issue: {issue_key}, Comment ID: {comment_id}"
                )

                # Fetch the original comment to get author and body
                jira_client = get_jira_client()
                comments = jira_client.get_issue_comments(issue_key)
                original_comment = next((c for c in comments if c["id"] == comment_id), None)

                if not original_comment:
                    logger.warning(
                        f"Comment not found - Issue: {issue_key}, Comment ID: {comment_id}, "
                        f"User: {user_id}"
                    )
                    await query.edit_message_text("Comment not found.")
                    return

                logger.info(
                    f"Original comment fetched - Issue: {issue_key}, Comment ID: {comment_id}, "
                    f"Author: {original_comment['author']}, "
                    f"Body length: {len(original_comment['body'])}"
                )

                # Store pending reply with original comment details
                pending_replies[user_id] = {
                    "issue_key": issue_key,
                    "comment_id": comment_id,
                    "original_author": original_comment["author"],
                    "original_author_account_id": original_comment.get("author_account_id"),
                    "original_body": original_comment["body"],
                }

                logger.debug(
                    f"Pending reply stored - User: {user_id}, Issue: {issue_key}, "
                    f"Comment ID: {comment_id}"
                )

                await query.edit_message_text(
                    f"💬 <b>Reply to comment on {issue_key}</b>\n\n"
                    f"Replying to: <b>{original_comment['author']}</b>\n\n"
                    f"Please type your reply message. I'll add it as a reply to the comment.\n\n"
                    f"Type /cancel to cancel.",
                    parse_mode=ParseMode.HTML,
                )

    elif data.startswith("view_comment_"):
        # Handle view full comment - show full comment details
        # Format: view_comment_ISSUE-KEY|COMMENT_ID
        data_parts = data.replace("view_comment_", "")
        if "|" in data_parts:
            parts = data_parts.split("|", 1)
            if len(parts) == 2:
                issue_key = parts[0]
                comment_id = parts[1]

                jira_client = get_jira_client()
                comments = jira_client.get_issue_comments(issue_key)

                # Find the specific comment
                comment = next((c for c in comments if c["id"] == comment_id), None)

                if not comment:
                    await query.edit_message_text("Comment not found.")
                    return

                # Format full comment details
                message = "<b>💬 Full Comment Details</b>\n\n"
                message += f"<b>Author:</b> {comment['author']}\n"
                message += f"<b>Created:</b> {comment['created']}\n"
                message += f"<b>Issue:</b> {issue_key}\n\n"
                message += f"<b>Comment:</b>\n{comment['body']}\n\n"

                # Add buttons to go back to comments list or reply
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "↩️ Reply", callback_data=f"reply_{issue_key}|{comment_id}"
                        ),
                        InlineKeyboardButton(
                            "🔙 Back to Comments", callback_data=f"comments_{issue_key}"
                        ),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text(
                    message, parse_mode=ParseMode.HTML, reply_markup=reply_markup
                )

    elif data.startswith("view_"):
        # Handle back button - show issue details again
        issue_key = data.replace("view_", "")
        jira_client = get_jira_client()
        issue = jira_client.get_issue(issue_key)

        if not issue:
            await query.edit_message_text(f"Could not find issue {issue_key}.")
            return

        message = f"""
🎫 <b>{issue["key"]}</b>

<b>Summary:</b> {issue["summary"]}

<b>Status:</b> {issue["status"]}
<b>Priority:</b> {issue["priority"]}
<b>Assignee:</b> {issue["assignee"]}
<b>Reporter:</b> {issue["reporter"]}

<b>Description:</b>
{issue["description"][:500]}{"..." if len(issue["description"]) > 500 else ""}

<b>Created:</b> {issue["created"][:10]}
<b>Updated:</b> {issue["updated"][:10]}

<a href="{issue["url"]}">View in Jira</a>
        """

        keyboard = [
            [
                InlineKeyboardButton("📝 Add Comment", callback_data=f"comment_{issue_key}"),
                InlineKeyboardButton("💬 View Comments", callback_data=f"comments_{issue_key}"),
            ],
            [InlineKeyboardButton("🔗 Open in Jira", url=issue["url"])],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(message, parse_mode=ParseMode.HTML, reply_markup=reply_markup)


async def handle_reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle reply messages for comments."""
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id

    if not is_authorized(user_id):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return

    # Check if user has a pending reply
    if user_id not in pending_replies:
        return

    reply_text = update.message.text.strip()
    username = update.effective_user.username or update.effective_user.first_name

    logger.info(
        f"Reply message received - User: {user_id} ({username}), "
        f"Reply text length: {len(reply_text)}"
    )

    # Handle cancel command
    if reply_text.lower() in ["/cancel", "cancel"]:
        logger.info(f"Reply cancelled by user - User: {user_id} ({username})")
        del pending_replies[user_id]
        await update.message.reply_text("❌ Reply cancelled.")
        return

    # Get pending reply info
    pending = pending_replies[user_id]
    issue_key = pending["issue_key"]
    comment_id = pending["comment_id"]
    original_author = pending.get("original_author", "Unknown")
    original_author_account_id = pending.get("original_author_account_id")

    logger.debug(
        f"Processing reply - User: {user_id}, Issue: {issue_key}, "
        f"Comment ID: {comment_id}, Original author: {original_author}, "
        f"Account ID: {original_author_account_id}"
    )

    # Clear pending reply
    del pending_replies[user_id]

    await update.message.reply_text(f"Adding reply to comment on {issue_key}...")

    # Format mention text (if available) - will be tried by reply_to_comment
    # The reply_to_comment method will try multiple formats automatically
    mention_text = None
    if original_author_account_id:
        # Use account ID format: [~accountid] (preferred for Jira Cloud)
        mention_text = f"[~{original_author_account_id}] "
        logger.debug(f"Using account ID mention: {original_author_account_id}")
    else:
        # Fallback: use plain text with author name (no mention format)
        # Some Jira instances don't support display name mentions
        mention_text = f"Replying to {original_author}: "
        logger.debug("Using plain text mention (no account ID available)")

    logger.info(
        f"Sending reply to Jira - Issue: {issue_key}, Comment ID: {comment_id}, "
        f"Reply length: {len(reply_text)}, User: {user_id}, "
        f"Mention available: {mention_text is not None}"
    )
    logger.debug(f"Reply text: {reply_text}")
    logger.debug(f"Mention text: {mention_text}")

    jira_client = get_jira_client()
    success = jira_client.reply_to_comment(issue_key, comment_id, reply_text, mention_text)

    if success:
        logger.info(
            f"Reply added successfully - Issue: {issue_key}, Comment ID: {comment_id}, "
            f"User: {user_id} ({username})"
        )
        await update.message.reply_text(f"✅ Reply added successfully to comment on {issue_key}!")
    else:
        logger.error(
            f"Failed to add reply - Issue: {issue_key}, Comment ID: {comment_id}, "
            f"User: {user_id} ({username}), Reply text: {reply_text[:100]}"
        )
        await update.message.reply_text(
            f"❌ Failed to add reply to comment on {issue_key}. Please try again."
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    print(f"Update {update} caused error {context.error}")
