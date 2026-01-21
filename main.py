#!/usr/bin/env python3
"""
Main entry point for running the Jira-Telegram bot.

This file is kept in the root for backward compatibility.
It imports and runs the main function from the package.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from jira_gram.main import main  # noqa: E402

if __name__ == "__main__":
    main()
