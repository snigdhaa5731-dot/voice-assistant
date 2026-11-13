"""
Natural Language Understanding (NLU) Engine.
Parses user intents and extracts entities from free-form spoken language.
"""

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, Optional


class IntentType(Enum):
    GREETING = auto()
    TIME = auto()
    DATE = auto()
    DATETIME = auto()
    WEB_SEARCH = auto()
    WEATHER = auto()
    REMINDER = auto()
    EMAIL = auto()
    QA = auto()
    ADD_COMMAND = auto()
    LIST_COMMANDS = auto()
    CUSTOM_COMMAND = auto()
    HELP = auto()
    EXIT = auto()
    UNKNOWN = auto()


@dataclass
class ParsedIntent:
    intent: IntentType
    raw_text: str
    confidence: float = 1.0
    entities: Dict[str, Any] = field(default_factory=dict)


class NLUEngine:
    """NLU engine using tokenization, pattern scoring, and entity extraction."""

    def __init__(self, custom_command_manager=None):
        self.custom_mgr = custom_command_manager
        self._init_patterns()

    def _init_patterns(self):
        # Exit patterns
        self.exit_patterns = [
            r"\b(exit|quit|stop|goodbye|bye|shut down|terminate|close assistant)\b"
        ]

        # Greeting patterns
        self.greeting_patterns = [
            r"^(hello|hi|hey|greetings|howdy|good (morning|afternoon|evening))\b",
            r"\b(how are you|how is it going|what'?s up|nice to meet you)\b",
        ]

        # Time & Date patterns
        self.datetime_patterns = [
            r"\b(date and time|time and date|what is today's date and time)\b"
        ]
        self.time_patterns = [
            r"\b(what('?s| is) the time|current time|tell me the time|what time is it|give me the time)\b"
        ]
        self.date_patterns = [
            r"\b(what('?s| is) (today'?s date|the date)|today'?s date|which day is today|what day is it)\b"
        ]

        # Web search patterns
        self.search_patterns = [
            r"^(?:please )?(?:search(?: the web)? for|google|look up|search for|find on web|find online)\s+(.+)",
            r"^(?:please )?search\s+(.+)",
        ]

        # Weather patterns
        self.weather_patterns = [
            r"\bweather\b",
            r"\btemperature\b",
            r"\bforecast\b",
            r"\bis it raining\b",
            r"\bhow is it outside\b",
        ]

        # Reminder patterns
        self.reminder_patterns = [
            r"\b(remind me|set a reminder|timer for|set a timer)\b"
        ]

        # Email patterns
        self.email_patterns = [
            r"\b(send (?:an )?email|mail to|compose email|voice email)\b"
        ]

        # QA / General knowledge patterns
        self.qa_patterns = [
            r"^(?:who is|who was|what is|what was|what are|define|explain|tell me about|where is|how does)\s+(.+)",
        ]

        # Custom commands patterns
        self.add_cmd_patterns = [
            r"^(?:add|create|register|new)\s+(?:custom )?command\b",
        ]
        self.list_cmd_patterns = [
            r"\b(list|show|view)\s+(?:custom )?commands\b",
            r"\bwhat (?:custom )?commands do you have\b",
        ]

        # Help patterns
        self.help_patterns = [
            r"\b(help|what can you do|features|instructions|options|commands)\b"
        ]

    def parse(self, text: str) -> ParsedIntent:
        """Parse raw user utterance into structured ParsedIntent."""
        clean = text.strip()
        lower = clean.lower()

        if not lower:
            return ParsedIntent(intent=IntentType.UNKNOWN, raw_text=clean, confidence=0.0)

        # 1. Exit / Quit
        for pattern in self.exit_patterns:
            if re.search(pattern, lower):
                return ParsedIntent(intent=IntentType.EXIT, raw_text=clean)

        # 2. Check Custom Commands first if registered
        if self.custom_mgr:
            match = self.custom_mgr.find_match(lower)
            if match:
                trigger, response = match
                return ParsedIntent(
                    intent=IntentType.CUSTOM_COMMAND,
                    raw_text=clean,
                    entities={"trigger": trigger, "response": response},
                )

        # 3. Add Custom Command
        for pattern in self.add_cmd_patterns:
            if re.search(pattern, lower):
                entities = self._extract_add_command_entities(clean)
                return ParsedIntent(intent=IntentType.ADD_COMMAND, raw_text=clean, entities=entities)

        # 4. List Custom Commands
        for pattern in self.list_cmd_patterns:
            if re.search(pattern, lower):
                return ParsedIntent(intent=IntentType.LIST_COMMANDS, raw_text=clean)

        # 5. Help
        for pattern in self.help_patterns:
            if re.fullmatch(pattern, lower) or lower in ("help", "features"):
                return ParsedIntent(intent=IntentType.HELP, raw_text=clean)

        # 6. Combined Date & Time
        for pattern in self.datetime_patterns:
            if re.search(pattern, lower):
                return ParsedIntent(intent=IntentType.DATETIME, raw_text=clean)

        # 7. Time
        for pattern in self.time_patterns:
            if re.search(pattern, lower):
                return ParsedIntent(intent=IntentType.TIME, raw_text=clean)

        # 8. Date
        for pattern in self.date_patterns:
            if re.search(pattern, lower):
                return ParsedIntent(intent=IntentType.DATE, raw_text=clean)

        # 9. Reminder / Timer
        for pattern in self.reminder_patterns:
            if re.search(pattern, lower):
                entities = self._extract_reminder_entities(clean)
                return ParsedIntent(intent=IntentType.REMINDER, raw_text=clean, entities=entities)

        # 10. Email
        for pattern in self.email_patterns:
            if re.search(pattern, lower):
                entities = self._extract_email_entities(clean)
                return ParsedIntent(intent=IntentType.EMAIL, raw_text=clean, entities=entities)

        # 11. Weather
        for pattern in self.weather_patterns:
            if re.search(pattern, lower):
                entities = self._extract_weather_entities(clean)
                return ParsedIntent(intent=IntentType.WEATHER, raw_text=clean, entities=entities)

        # 12. Explicit Web Search
        for pattern in self.search_patterns:
            match = re.search(pattern, clean, re.IGNORECASE)
            if match:
                query = match.group(1).strip()
                return ParsedIntent(
                    intent=IntentType.WEB_SEARCH,
                    raw_text=clean,
                    entities={"query": query},
                )

        # 13. Greeting
        for pattern in self.greeting_patterns:
            if re.search(pattern, lower):
                return ParsedIntent(intent=IntentType.GREETING, raw_text=clean)

        # 14. QA / Informational queries ("Who is...", "What is...")
        for pattern in self.qa_patterns:
            match = re.search(pattern, clean, re.IGNORECASE)
            if match:
                subject = match.group(1).rstrip("?.! ")
                return ParsedIntent(
                    intent=IntentType.QA,
                    raw_text=clean,
                    entities={"query": subject},
                )

        # 15. Default fallback: If query looks like an inquiry, treat as QA or Web Search
        words = lower.split()
        if len(words) > 1 and any(words[0].startswith(q) for q in ["who", "what", "where", "why", "how"]):
            return ParsedIntent(
                intent=IntentType.QA,
                raw_text=clean,
                entities={"query": clean.rstrip("?.!")},
            )

        # Unknown intent
        return ParsedIntent(intent=IntentType.UNKNOWN, raw_text=clean, confidence=0.3)

    def _extract_weather_entities(self, text: str) -> Dict[str, Any]:
        """Extract city/location from weather utterances."""
        # Strip trailing punctuation
        cleaned = re.sub(r"[^\w\s]", "", text).lower().strip()
        match = re.search(r"\b(?:in|for|at)\s+([a-z\s]+?)(?:\s+(?:today|tomorrow|now))?$", cleaned)
        if match:
            city = match.group(1).strip().title()
            return {"city": city}
        return {"city": None}

    def _extract_reminder_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract duration (in seconds) and reminder message.
        Examples:
            'remind me in 10 seconds to stretch'
            'set a reminder for 5 minutes to call mom'
            'timer for 30 seconds'
        """
        lower = text.lower()
        duration_seconds = 0
        message = "Time is up!"

        # Extract number + unit
        match = re.search(r"(\d+)\s*(seconds?|secs?|minutes?|mins?|hours?|hrs?)", lower)
        if match:
            value = int(match.group(1))
            unit = match.group(2)
            if "sec" in unit:
                duration_seconds = value
            elif "min" in unit:
                duration_seconds = value * 60
            elif "hr" in unit or "hour" in unit:
                duration_seconds = value * 3600

        # Extract message: e.g. "to <do something>"
        task_match = re.search(r"\bto\s+(.+)$", text, re.IGNORECASE)
        if task_match:
            message = task_match.group(1).strip()

        return {
            "duration": duration_seconds,
            "message": message,
        }

    def _extract_email_entities(self, text: str) -> Dict[str, Any]:
        """Extract recipient, subject, and body from email speech command."""
        # Find email address if present
        email_match = re.search(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", text)
        recipient = email_match.group(1) if email_match else None

        # Check for subject: "subject <sub content> and body/message <content>"
        subj_match = re.search(r"subject\s+(.+?)(?:\s+(?:and )?(?:body|message)\s+(.+))?$", text, re.IGNORECASE)
        subject = None
        body = None
        if subj_match:
            subject = subj_match.group(1).strip()
            if subj_match.group(2):
                body = subj_match.group(2).strip()

        return {
            "recipient": recipient,
            "subject": subject,
            "body": body,
        }

    def _extract_add_command_entities(self, text: str) -> Dict[str, Any]:
        """
        Try to extract trigger and response from one command:
        e.g. "add command [trigger] as/with response [response]" or "add command [trigger] to [response]"
        """
        pattern = r"^(?:add|create|register)\s+(?:custom )?command\s+(.+?)\s+(?:as|with response|to)\s+(.+)$"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return {
                "trigger": match.group(1).strip(),
                "response": match.group(2).strip(),
            }
        return {"trigger": None, "response": None}
