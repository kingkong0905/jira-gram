"""
Setup script for jira-gram package.

Configuration is in pyproject.toml
"""

from setuptools import find_packages, setup

setup(
    name="jira-gram",
    version="1.0.0",
    description="Telegram bot for Jira integration with FastAPI",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "pydantic>=2.5.3",
        "pydantic-settings>=2.1.0",
        "python-telegram-bot>=20.7",
        "jira>=3.8.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "python-dateutil>=2.8.2",
        "structlog>=24.1.0",
    ],
)
