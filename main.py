"""FastAPI application for Telegram Jira Bot."""

from fastapi import FastAPI, Request, Response
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
import uvicorn
import config
from bot_handlers import (
    start_command,
    view_command,
    comment_command,
    search_command,
    button_callback,
    error_handler,
)

# Validate configuration
config.validate_config()

# Initialize FastAPI app
app = FastAPI(title="Jira Telegram Bot")

# Initialize Telegram bot application
telegram_app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

# Register handlers
telegram_app.add_handler(CommandHandler("start", start_command))
telegram_app.add_handler(CommandHandler("view", view_command))
telegram_app.add_handler(CommandHandler("comment", comment_command))
telegram_app.add_handler(CommandHandler("search", search_command))
telegram_app.add_handler(CallbackQueryHandler(button_callback))
telegram_app.add_error_handler(error_handler)


@app.on_event("startup")
async def on_startup():
    """Initialize bot on startup."""
    await telegram_app.initialize()
    await telegram_app.start()

    # Set webhook if WEBHOOK_URL is configured
    if config.WEBHOOK_URL:
        webhook_url = f"{config.WEBHOOK_URL}{config.WEBHOOK_PATH}"
        await telegram_app.bot.set_webhook(url=webhook_url)
        print(f"Webhook set to: {webhook_url}")
    else:
        print("Warning: WEBHOOK_URL not configured. Bot will not receive updates.")
        print(
            "Either set WEBHOOK_URL in .env or use polling mode for local development."
        )


@app.on_event("shutdown")
async def on_shutdown():
    """Clean up on shutdown."""
    await telegram_app.stop()
    await telegram_app.shutdown()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "running", "bot": "Jira Telegram Bot", "version": "1.0.0"}


@app.post(config.WEBHOOK_PATH)
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
    print(f"Server running on {config.HOST}:{config.PORT}")

    uvicorn.run("main:app", host=config.HOST, port=config.PORT, reload=True)


if __name__ == "__main__":
    main()
