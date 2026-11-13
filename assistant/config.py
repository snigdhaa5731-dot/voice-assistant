"""
Configuration management for the Voice Assistant.
Loads environment variables from .env with fallback defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Assistant Identity
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "Aura")

# Text-to-Speech Settings
TTS_RATE = int(os.getenv("TTS_RATE", "175"))
TTS_VOLUME = float(os.getenv("TTS_VOLUME", "1.0"))

# Weather API Settings
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "New York")

# Email / SMTP Settings
MOCK_EMAIL = os.getenv("MOCK_EMAIL", "true").strip().lower() in ("true", "1", "yes")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
DEFAULT_RECIPIENT = os.getenv("DEFAULT_RECIPIENT", "user@example.com")

# Custom Commands Storage
CUSTOM_COMMANDS_PATH = BASE_DIR / "custom_commands.json"
