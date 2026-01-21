"""
Setup script for jira-gram package.

Configuration is in pyproject.toml
"""

from setuptools import find_packages, setup

setup(
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
