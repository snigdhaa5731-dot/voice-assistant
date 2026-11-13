"""
Custom Commands Manager.
Allows users to add, list, and trigger custom commands via JSON config or runtime/voice.
"""

import json
import os
import webbrowser
from pathlib import Path
from typing import Dict, Optional, Tuple

from .config import CUSTOM_COMMANDS_PATH


DEFAULT_CUSTOM_COMMANDS = {
    "tell me a joke": "Why do programmers prefer dark mode? Because light attracts bugs!",
    "who made you": "I was built as a Python Voice Assistant with speech recognition and natural language processing.",
    "what is your name": "My name is Aura, your personal Python voice assistant.",
    "open github": "https://github.com",
    "quote": "The only way to do great work is to love what you do. — Steve Jobs",
}


class CustomCommandManager:
    """Manages custom user-defined commands stored in a JSON configuration."""

    def __init__(self, filepath: Path = CUSTOM_COMMANDS_PATH):
        self.filepath = Path(filepath)
        self.commands: Dict[str, str] = {}
        self.load()

    def load(self) -> None:
        """Load custom commands from JSON file, initializing if missing or empty."""
        if not self.filepath.exists() or self.filepath.stat().st_size == 0:
            self.commands = dict(DEFAULT_CUSTOM_COMMANDS)
            self.save()
            return

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self.commands = {k.strip().lower(): str(v).strip() for k, v in data.items()}
                else:
                    self.commands = dict(DEFAULT_CUSTOM_COMMANDS)
        except Exception as e:
            print(f"[Warning] Error loading custom commands from {self.filepath}: {e}")
            self.commands = dict(DEFAULT_CUSTOM_COMMANDS)

    def save(self) -> bool:
        """Save current custom commands back to JSON file."""
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.commands, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[Error] Failed to save custom commands: {e}")
            return False

    def add_command(self, trigger: str, response: str) -> bool:
        """Add or update a custom command."""
        trigger_clean = trigger.strip().lower()
        response_clean = response.strip()
        if not trigger_clean or not response_clean:
            return False
        self.commands[trigger_clean] = response_clean
        return self.save()

    def remove_command(self, trigger: str) -> bool:
        """Remove a custom command."""
        trigger_clean = trigger.strip().lower()
        if trigger_clean in self.commands:
            del self.commands[trigger_clean]
            return self.save()
        return False

    def find_match(self, text: str) -> Optional[Tuple[str, str]]:
        """
        Check if any custom command matches the given query text.
        Returns (trigger, response) or None.
        """
        clean = text.strip().lower()
        # Direct exact match
        if clean in self.commands:
            return clean, self.commands[clean]

        # Substring / phrase match
        for trigger, response in self.commands.items():
            if trigger in clean:
                return trigger, response

        return None

    def execute_response(self, response: str) -> Tuple[str, bool]:
        """
        Determines if response is a URL to open or spoken text.
        Returns (message, was_url).
        """
        if response.startswith("http://") or response.startswith("https://"):
            try:
                webbrowser.open(response)
                return f"Opening {response} in your web browser.", True
            except Exception as e:
                return f"Failed to open URL: {e}", False
        return response, False
