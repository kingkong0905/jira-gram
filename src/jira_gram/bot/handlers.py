"""Telegram bot handlers for Jira integration."""

import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from jira_gram.config import get_settings
from jira_gram.jira import JiraClient

from .auth import is_authorized


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

        message = f"<b>💬 Comments for {issue_key}:</b>\n\n"

        for i, comment in enumerate(comments[:5], 1):  # Limit to 5 most recent
            message += f"<b>{i}. {comment['author']}</b> ({comment['created'][:10]})\n"
            comment_body = comment["body"][:200]
            message += f"{comment_body}{'...' if len(comment['body']) > 200 else ''}\n\n"

        if len(comments) > 5:
            message += f"<i>... and {len(comments) - 5} more comments</i>"

        await query.edit_message_text(message, parse_mode=ParseMode.HTML)

    elif data.startswith("comment_"):
        issue_key = data.replace("comment_", "")
        await query.edit_message_text(
            f"To add a comment to {issue_key}, use:\n\n"
            f"`/comment {issue_key} Your comment here`",
            parse_mode=ParseMode.MARKDOWN,
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    print(f"Update {update} caused error {context.error}")
