"""
Unit tests for CustomCommandManager.
"""

import tempfile
from pathlib import Path
import unittest

from assistant.custom_cmds import CustomCommandManager


class TestCustomCommands(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.mgr = CustomCommandManager(filepath=Path(self.temp_file.name))

    def tearDown(self):
        Path(self.temp_file.name).unlink(missing_ok=True)

    def test_add_and_match_command(self):
        self.mgr.add_command("ping", "pong")
        match = self.mgr.find_match("ping")
        self.assertIsNotNone(match)
        self.assertEqual(match[1], "pong")

    def test_case_insensitive_matching(self):
        self.mgr.add_command("Open Portal", "https://portal.example.com")
        match = self.mgr.find_match("please open portal now")
        self.assertIsNotNone(match)
        self.assertEqual(match[1], "https://portal.example.com")

    def test_remove_command(self):
        self.mgr.add_command("to_remove", "value")
        self.assertTrue(self.mgr.remove_command("to_remove"))
        self.assertIsNone(self.mgr.find_match("to_remove"))

    def test_persistence(self):
        self.mgr.add_command("persist_key", "persist_value")
        # Reload in a new manager instance
        new_mgr = CustomCommandManager(filepath=Path(self.temp_file.name))
        match = new_mgr.find_match("persist_key")
        self.assertIsNotNone(match)
        self.assertEqual(match[1], "persist_value")


if __name__ == "__main__":
    unittest.main()
