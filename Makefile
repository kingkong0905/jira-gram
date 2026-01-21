.PHONY: help install install-dev test coverage lint format clean run dev

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt
	pip install -e .

install-dev:  ## Install development dependencies
	pip install -r requirements.txt
	pip install -e ".[dev]"

test:  ## Run tests
	PYTHONPATH=src pytest tests/ -v

test-watch:  ## Run tests in watch mode
	PYTHONPATH=src pytest-watch tests/

coverage:  ## Run tests with coverage report
	PYTHONPATH=src pytest tests/ --cov=jira_gram --cov-report=term-missing --cov-report=html

lint:  ## Run linters
	flake8 src/ tests/ --max-line-length=100 --exclude=__pycache__,.venv,build,dist
	mypy src/jira_gram --ignore-missing-imports

format:  ## Format code with black and isort
	black src/ tests/ --line-length=100
	isort src/ tests/

format-check:  ## Check code formatting
	black src/ tests/ --check --line-length=100
	isort src/ tests/ --check-only

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete

run:  ## Run the application
	PYTHONPATH=src python -m jira_gram.main

dev:  ## Run the application in development mode with auto-reload
	PYTHONPATH=src uvicorn jira_gram.main:app --reload --host 0.0.0.0 --port 8000

# Heroku deployment
heroku-login:  ## Login to Heroku
	heroku login

heroku-create:  ## Create Heroku app
	heroku create

heroku-deploy:  ## Deploy to Heroku
	git push heroku main

heroku-logs:  ## View Heroku logs
	heroku logs --tail

heroku-config:  ## Show Heroku config
	heroku config

# Docker commands (if needed)
docker-build:  ## Build Docker image
	docker build -t jira-gram .

docker-run:  ## Run Docker container
	docker run -p 8000:8000 --env-file .env jira-gram
