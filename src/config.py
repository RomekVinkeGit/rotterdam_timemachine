"""Configuration management for the Rotterdam Time Machine project.

This module provides centralized configuration management for the Rotterdam Time Machine
application. It handles environment variables, file paths, and application settings.

The module loads configuration from environment variables and provides default values
for application settings. It also ensures that required directories exist.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "articles.db"

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")

# OpenAI Configuration
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_TEMPERATURE = 0.2

# Database Configuration
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Wikipedia API Configuration
WIKIPEDIA_LANG = "nl"
WIKIPEDIA_MAX_RESULTS = 3
WIKIPEDIA_CHAR_LIMIT = 4000

# Application Settings
MAX_KEYWORDS = 5
MAX_CONTEXT_ITEMS = 3

# Ensure required directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True) 