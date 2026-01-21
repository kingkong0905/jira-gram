# Jira Telegram Bot

A Telegram bot built with FastAPI that allows you to view, comment on, and interact with Jira tickets directly from Telegram.

## ⚡ Quick Start

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone <repository-url>
cd jira-gram

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run the bot
uv run python main.py
```

Or use the Makefile:
```bash
make install  # Install dependencies
make run      # Run the bot
```

## Features

- 🔍 **View Jira Tickets**: Get detailed information about any Jira issue
- 💬 **Add Comments**: Comment on Jira issues directly from Telegram
- 🔎 **Search Issues**: Search for Jira issues using JQL (Jira Query Language)
- 📝 **View Comments**: Read existing comments on tickets
- 🔒 **Access Control**: Optional user authorization

## Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer (recommended) or pip
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Jira Account with API access
- Jira API Token ([Create one here](https://id.atlassian.com/manage-profile/security/api-tokens))

## Installation

### Option 1: Using uv (Recommended - Fast!)

1. **Install uv** (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or on macOS: brew install uv
# Or on Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. **Clone the repository**:
```bash
git clone <repository-url>
cd jira-gram
```

3. **Install dependencies and create virtual environment**:
```bash
uv sync
```

4. **Configure environment variables**:
```bash
cp .env.example .env
```

### Option 2: Using pip

1. **Clone the repository**:
```bash
git clone <repository-url>
cd jira-gram
```

2. **Create a virtual environment**:
```bash
python -m venv venv
**With uv:**
```bash
uv run python main.py
# Or activate the virtual environment first:
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python main.py
```

**With pip:**
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```

Note: In local development, you can leave `WEBHOOK_URL` empty. For production, you need to set up a webhook.

### Production (Webhook Mode)

1. Deploy to a server with a public URL
2. Set `WEBHOOK_URL` in `.env` to your public URL
3. Run with:

**With uv:**
```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

**Or use a production server like Gunicorn:**
```bash
uv run gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**With pip:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
# Or with Gunicorn:_URL=https://your-domain.com/webhook  # For production
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your_email@example.com
JIRA_API_TOKEN=your_jira_api_token
```

## Usage

### Local Development (Polling Mode)

For local development without webhooks:

```bash
python main.py
```

Note: In local development, you can leave `WEBHOOK_URL` empty. For production, you need to set up a webhook.

### Production (Webhook Mode)

1. Deploy to a server with a public URL
2. Set `WEBHOOK_URL` in `.env` to your public URL
3. Run with:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Or use a production server like Gunicorn:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Bot Commands

### `/start`
Shows welcome message and available commands

### `/view <ISSUE-KEY>`
View detailed information about a Jira ticket

**Example:**
```
/view PROJ-123
```

### `/comment <ISSUE-KEY> <comment text>`
Add a comment to a Jira ticket

**Example:**
```
/comment PROJ-123 This issue has been resolved
```

### `/search <JQL query>`
Search for Jira issues using JQL

**Examples:**
```
/search assignee = currentUser() AND status = "In Progress"
/search project = PROJ AND status = Open
/search priority = High
```

## API Endpoints

- `GET /` - Root endpoint with bot information
- `GET /health` - Health check endpoint
- `POST /webhook` - Webhook endpoint for Telegram updates

## Configuration Options

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | Your Telegram bot token |
| `WEBHOOK_URL` | Production | Public URL for webhook (e.g., https://yourdomain.com) |
| `WEBHOOK_PATH` | No | Webhook path (default: `/webhook`) |
| `JIRA_URL` | Yes | Your Jira instance URL |
| `JIRA_EMAIL` | Yes | Your Jira account email |
| `JIRA_API_TOKEN` | Yes | Your Jira API token |
| `HOST` | No | Server host (default: `0.0.0.0`) |
| `PORT` | No | Server port (default: `8000`) |
| `ALLOWED_USERS` | No | Comma-separated list of allowed Telegram user IDs |

### Access Control

To restrict bot access to specific users, add their Telegram user IDs to `ALLOWED_USERS`:

```env
ALLOWED_USERS=123456789,987654321
```

To find your Telegram user ID, use [@userinfobot](https://t.me/userinfobot).

## Project Structure

```
jira-gram/
├── main.py              # FastAPI application and webhook handler
├── config.py            # Configuration management
├── jira_client.py       # Jira API client
├── bot_handlers.py      # Telegram bot command handlers
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## Deployment
Quick Commands with Makefile

```bash
make install    # Install dependencies
make run        # Run the bot
make dev        # Run with auto-reload
make test       # Run tests
make lint       # Run linting
make format     # Format code
make clean      # Clean up files
make help       # Show all commands
```

### Manual Commands

**Running Tests:**
```bash
uv run pytest  # With uv
pytest         # With pip (after activating venv)
```

**Code Formatting:**
```bash
uv run black .  # With uv
black .         # With pip
```

**Linting:**
```bash
uv run flake8 .  # With uv
flake8 .         # With pip the repository
3. Install dependencies
4. Set up a reverse proxy (nginx/Caddy) for HTTPS
5. Use systemd or supervisor to run the bot

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
```

### Linting
```bash
flake8 .
```

## Troubleshooting

### Bot doesn't respond
- Check if `TELEGRAM_BOT_TOKEN` is correct
- Verify webhook is set correctly with `https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
- Check server logs for errors

### Jira connection issues
- Verify `JIRA_URL`, `JIRA_EMAIL`, and `JIRA_API_TOKEN` are correct
- Check if API token has necessary permissions
- Ensure Jira URL includes `https://` and doesn't end with `/`

### Webhook not working
- Ensure `WEBHOOK_URL` is publicly accessible via HTTPS
- Telegram requires HTTPS for webhooks
- Check if port is open and accessible

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
