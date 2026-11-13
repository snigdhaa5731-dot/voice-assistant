"""
Unit tests for NLU intent parsing and entity extraction.
"""

import unittest
from assistant.nlu import NLUEngine, IntentType
from assistant.custom_cmds import CustomCommandManager


class TestNLUEngine(unittest.TestCase):

    def setUp(self):
        self.custom_mgr = CustomCommandManager()
        self.nlu = NLUEngine(custom_command_manager=self.custom_mgr)

    def test_greeting_intents(self):
        phrases = ["hello", "hi there", "hey aura", "good morning", "how are you"]
        for p in phrases:
            res = self.nlu.parse(p)
            self.assertEqual(res.intent, IntentType.GREETING, f"Failed on: {p}")

    def test_time_and_date_intents(self):
        res = self.nlu.parse("what time is it")
        self.assertEqual(res.intent, IntentType.TIME)

        res = self.nlu.parse("what is today's date")
        self.assertEqual(res.intent, IntentType.DATE)

        res = self.nlu.parse("tell me the date and time")
        self.assertEqual(res.intent, IntentType.DATETIME)

    def test_web_search_intent(self):
        res = self.nlu.parse("search for python programming tutorials")
        self.assertEqual(res.intent, IntentType.WEB_SEARCH)
        self.assertIn("python programming tutorials", res.entities.get("query", ""))

        res2 = self.nlu.parse("google machine learning courses")
        self.assertEqual(res2.intent, IntentType.WEB_SEARCH)
        self.assertIn("machine learning courses", res2.entities.get("query", ""))

    def test_weather_intent(self):
        res = self.nlu.parse("what is the weather in London")
        self.assertEqual(res.intent, IntentType.WEATHER)
        self.assertEqual(res.entities.get("city"), "London")

        res_punct = self.nlu.parse("what is the weather in London?")
        self.assertEqual(res_punct.intent, IntentType.WEATHER)
        self.assertEqual(res_punct.entities.get("city"), "London")

        res2 = self.nlu.parse("how is the weather outside")
        self.assertEqual(res2.intent, IntentType.WEATHER)

    def test_reminder_intent(self):
        res = self.nlu.parse("remind me in 30 seconds to take a break")
        self.assertEqual(res.intent, IntentType.REMINDER)
        self.assertEqual(res.entities.get("duration"), 30)
        self.assertEqual(res.entities.get("message"), "take a break")

        res2 = self.nlu.parse("set a reminder for 5 minutes to stretch")
        self.assertEqual(res2.intent, IntentType.REMINDER)
        self.assertEqual(res2.entities.get("duration"), 300)
        self.assertEqual(res2.entities.get("message"), "stretch")

    def test_email_intent(self):
        res = self.nlu.parse("send an email to test@example.com with subject Meeting and body Hello team")
        self.assertEqual(res.intent, IntentType.EMAIL)
        self.assertEqual(res.entities.get("recipient"), "test@example.com")
        self.assertEqual(res.entities.get("subject"), "Meeting")
        self.assertEqual(res.entities.get("body"), "Hello team")

    def test_qa_intent(self):
        res = self.nlu.parse("who was Albert Einstein")
        self.assertEqual(res.intent, IntentType.QA)
        self.assertIn("Albert Einstein", res.entities.get("query", ""))

        res2 = self.nlu.parse("what is photosynthesis")
        self.assertEqual(res2.intent, IntentType.QA)
        self.assertIn("photosynthesis", res2.entities.get("query", ""))

    def test_custom_command_matching(self):
        self.custom_mgr.add_command("test trigger", "test response")
        res = self.nlu.parse("test trigger")
        self.assertEqual(res.intent, IntentType.CUSTOM_COMMAND)
        self.assertEqual(res.entities.get("response"), "test response")

    def test_exit_intent(self):
        phrases = ["exit", "quit", "goodbye", "stop", "bye"]
        for p in phrases:
            res = self.nlu.parse(p)
            self.assertEqual(res.intent, IntentType.EXIT, f"Failed on: {p}")


if __name__ == "__main__":
    unittest.main()
