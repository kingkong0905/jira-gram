.PHONY: install run dev test lint format clean help

help:
	@echo "Available commands:"
	@echo "  make install   - Install dependencies using uv"
	@echo "  make run       - Run the bot in production mode"
	@echo "  make dev       - Run the bot in development mode with auto-reload"
	@echo "  make test      - Run tests"
	@echo "  make lint      - Run linting checks"
	@echo "  make format    - Format code with black"
	@echo "  make clean     - Remove virtual environment and cache files"

install:
	@echo "Installing dependencies with uv..."
	uv sync

run:
	@echo "Starting bot..."
	uv run python main.py

dev:
	@echo "Starting bot in development mode..."
	uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

test:
	@echo "Running tests..."
	uv run pytest

lint:
	@echo "Running linting..."
	uv run flake8 .

format:
	@echo "Formatting code..."
	uv run black .

clean:
	@echo "Cleaning up..."
	rm -rf .venv
	rm -rf __pycache__
	rm -rf .pytest_cache
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
