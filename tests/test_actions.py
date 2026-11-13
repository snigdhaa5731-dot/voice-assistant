"""
Unit tests for ActionHandler.
"""

import tempfile
from pathlib import Path
import unittest

from assistant.actions import ActionHandler
from assistant.custom_cmds import CustomCommandManager
from assistant.speech import TTSManager


class TestActionHandler(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.custom_mgr = CustomCommandManager(filepath=Path(self.temp_file.name))
        # Mute TTS for tests
        self.tts = TTSManager(muted=True)
        self.actions = ActionHandler(tts=self.tts, custom_mgr=self.custom_mgr)

    def tearDown(self):
        Path(self.temp_file.name).unlink(missing_ok=True)

    def test_greeting(self):
        res = self.actions.handle_greeting()
        self.assertIn("Aura", res)
        self.assertTrue(any(w in res for w in ["Good morning", "Good afternoon", "Good evening"]))

    def test_time(self):
        res = self.actions.handle_time()
        self.assertIn("The current time is", res)

    def test_date(self):
        res = self.actions.handle_date()
        self.assertIn("Today is", res)

    def test_datetime(self):
        res = self.actions.handle_datetime()
        self.assertIn("It is currently", res)

    def test_weather_fallback(self):
        res = self.actions.handle_weather("London")
        self.assertIn("London", res)

    def test_qa_query(self):
        res = self.actions.handle_qa("Python programming language")
        self.assertIsInstance(res, str)
        self.assertTrue(len(res) > 10)

    def test_mock_email(self):
        res = self.actions.handle_email(
            recipient="rahul@example.com",
            subject="Test Subject",
            body="Test Body Message",
        )
        self.assertIn("rahul@example.com", res)
        self.assertIn("sent successfully in test mode", res)

    def test_add_and_list_custom_commands(self):
        add_res = self.actions.handle_add_command(trigger="say hello", response="Hello back!")
        self.assertIn("Custom command added successfully", add_res)

        list_res = self.actions.handle_list_commands()
        self.assertIn("say hello", list_res)


if __name__ == "__main__":
    unittest.main()
