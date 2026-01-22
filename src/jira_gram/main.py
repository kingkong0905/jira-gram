"""FastAPI application for Telegram Jira Bot."""

import uvicorn
from fastapi import FastAPI, Request, Response
from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from jira_gram.bot import (
    button_callback,
    comment_command,
    error_handler,
    handle_reply_message,
    search_command,
    start_command,
    view_command,
)
from jira_gram.config import get_settings, validate_config

# Validate configuration
validate_config()
settings = get_settings()

# Initialize FastAPI app
app = FastAPI(title="Jira Telegram Bot", version="1.0.0")

# Initialize Telegram bot application
telegram_app = Application.builder().token(settings.telegram_bot_token).build()

# Register handlers
telegram_app.add_handler(CommandHandler("start", start_command))
telegram_app.add_handler(CommandHandler("view", view_command))
telegram_app.add_handler(CommandHandler("comment", comment_command))
telegram_app.add_handler(CommandHandler("search", search_command))
telegram_app.add_handler(CallbackQueryHandler(button_callback))
# Handle reply messages (must be after command handlers to avoid conflicts)
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reply_message))
telegram_app.add_error_handler(error_handler)


@app.on_event("startup")
async def on_startup():
    """Initialize bot on startup."""
    await telegram_app.initialize()
    await telegram_app.start()

    # Set webhook if WEBHOOK_URL is configured
    if settings.webhook_url:
        webhook_url = f"{settings.webhook_url}{settings.webhook_path}"
        await telegram_app.bot.set_webhook(url=webhook_url)
        print(f"Webhook set to: {webhook_url}")
    else:
        print("Warning: WEBHOOK_URL not configured. Bot will not receive updates.")
        print("Either set WEBHOOK_URL in .env or use polling mode for local development.")


@app.on_event("shutdown")
async def on_shutdown():
    """Clean up on shutdown."""
    await telegram_app.stop()
    await telegram_app.shutdown()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "running", "bot": "Jira Telegram Bot", "version": "1.0.0"}


@app.post(settings.webhook_path)
async def webhook(request: Request):
    """Handle incoming Telegram updates via webhook."""
    try:
        data = await request.json()
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.process_update(update)
        return Response(status_code=200)
    except Exception as e:
        print(f"Error processing update: {e}")
        return Response(status_code=500)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


def main():
    """Run the FastAPI server."""
    print("Starting Jira Telegram Bot...")
    print(f"Server running on {settings.host}:{settings.port}")

    uvicorn.run("jira_gram.main:app", host=settings.host, port=settings.port, reload=True)


if __name__ == "__main__":
    main()
