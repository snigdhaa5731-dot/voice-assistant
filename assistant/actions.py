"""
Actions handler for all Voice Assistant features.
Implements Beginner & Advanced tiers: greetings, time/date, web search,
weather, reminders with audible alerts, email sending (smtplib), QA, and custom commands.
"""

import datetime
import email.message
import smtplib
import threading
import time
import urllib.parse
import webbrowser
from typing import Callable, Optional
import requests

from .config import (
    ASSISTANT_NAME,
    DEFAULT_CITY,
    DEFAULT_RECIPIENT,
    MOCK_EMAIL,
    OPENWEATHER_API_KEY,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_SERVER,
    SMTP_USER,
)
from .custom_cmds import CustomCommandManager
from .speech import TTSManager


class ActionHandler:
    """Executes actions corresponding to parsed intents."""

    def __init__(self, tts: TTSManager, custom_mgr: CustomCommandManager):
        self.tts = tts
        self.custom_mgr = custom_mgr
        self.active_reminders = []

    def handle_greeting(self) -> str:
        """Beginner Tier: Respond to 'Hello' with a predefined greeting."""
        hour = datetime.datetime.now().hour
        if hour < 12:
            time_greet = "Good morning"
        elif hour < 18:
            time_greet = "Good afternoon"
        else:
            time_greet = "Good evening"

        response = f"{time_greet}! I am {ASSISTANT_NAME}, your personal voice assistant. How may I help you today?"
        self.tts.speak(response)
        return response

    def handle_time(self) -> str:
        """Beginner Tier: Tell the current time."""
        now = datetime.datetime.now()
        current_time = now.strftime("%I:%M %p")
        response = f"The current time is {current_time}."
        self.tts.speak(response)
        return response

    def handle_date(self) -> str:
        """Beginner Tier: Tell the current date."""
        now = datetime.datetime.now()
        current_date = now.strftime("%A, %B %d, %Y")
        response = f"Today is {current_date}."
        self.tts.speak(response)
        return response

    def handle_datetime(self) -> str:
        """Beginner Tier: Tell both current time and date."""
        now = datetime.datetime.now()
        msg = f"It is currently {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}."
        self.tts.speak(msg)
        return msg

    def handle_web_search(self, query: str) -> str:
        """Beginner Tier: Perform a web search on a user-specified topic (opens browser)."""
        query_clean = query.strip()
        if not query_clean:
            msg = "What would you like me to search for?"
            self.tts.speak(msg)
            return msg

        url = f"https://www.google.com/search?q={urllib.parse.quote(query_clean)}"
        msg = f"Searching the web for '{query_clean}'."
        self.tts.speak(msg)
        try:
            webbrowser.open(url)
        except Exception as e:
            msg = f"Opened search for {query_clean}, but browser reported: {e}"
        return msg

    def handle_weather(self, city: Optional[str] = None) -> str:
        """Advanced Tier: Fetch and read out live weather updates using a weather API."""
        target_city = city.strip() if city and city.strip() else DEFAULT_CITY

        # 1. Try OpenWeatherMap if API key is provided
        if OPENWEATHER_API_KEY:
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={urllib.parse.quote(target_city)}&appid={OPENWEATHER_API_KEY}&units=metric"
                res = requests.get(url, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    temp = round(data["main"]["temp"])
                    desc = data["weather"][0]["description"]
                    humidity = data["main"]["humidity"]
                    response = f"The weather in {target_city} is currently {desc} with a temperature of {temp} degrees Celsius and {humidity} percent humidity."
                    self.tts.speak(response)
                    return response
            except Exception as e:
                print(f"[Weather] OpenWeatherMap request error: {e}")

        # 2. Resilient Fallback: wttr.in JSON API (Requires no API key, completely free)
        try:
            url = f"https://wttr.in/{urllib.parse.quote(target_city)}?format=j1"
            res = requests.get(url, headers={"User-Agent": "VoiceAssistant/1.0"}, timeout=6)
            if res.status_code == 200:
                data = res.json()
                current = data["current_condition"][0]
                temp_c = current["temp_C"]
                desc = current["weatherDesc"][0]["value"]
                humidity = current["humidity"]
                response = f"The current weather in {target_city} is {desc} at {temp_c} degrees Celsius with {humidity} percent humidity."
                self.tts.speak(response)
                return response
        except Exception as e:
            print(f"[Weather] wttr.in fallback error: {e}")

        # 3. Fallback message if completely offline
        msg = f"I was unable to retrieve live weather data for {target_city}. Please check your internet connection or verify your OpenWeatherMap API key."
        self.tts.speak(msg)
        return msg

    def handle_reminder(self, duration_seconds: int, message: str) -> str:
        """Advanced Tier: Set a timed reminder that triggers an audible alert after a specified duration."""
        if duration_seconds <= 0:
            msg = "Please specify a valid duration for the reminder (for example, 10 seconds or 5 minutes)."
            self.tts.speak(msg)
            return msg

        msg = f"Reminder set for {duration_seconds} seconds from now: '{message}'."
        self.tts.speak(msg)

        def _trigger_reminder():
            time.sleep(duration_seconds)
            # Audible alert (system terminal bell & repeated voice alert)
            print("\a", end="", flush=True)
            alert = f"Attention! Reminder alert: {message}"
            print(f"\n🔔 [REMINDER ALERT] {alert}\n")
            self.tts.speak(alert)

        thread = threading.Thread(target=_trigger_reminder, daemon=True)
        thread.start()
        self.active_reminders.append(thread)
        return msg

    def handle_email(
        self,
        recipient: Optional[str] = None,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        input_fn: Optional[Callable[[str], str]] = None,
    ) -> str:
        """
        Advanced Tier: Send an email via voice command using smtplib.
        Supports real SMTP or test/dummy mock mode.
        """
        # Interactive prompts if missing parameters
        if not recipient:
            if input_fn:
                self.tts.speak("Who would you like to send the email to?")
                recipient = input_fn("Recipient Email: ").strip()
            if not recipient:
                recipient = DEFAULT_RECIPIENT

        if not subject:
            if input_fn:
                self.tts.speak("What is the subject of the email?")
                subject = input_fn("Subject: ").strip()
            if not subject:
                subject = "Voice Assistant Message"

        if not body:
            if input_fn:
                self.tts.speak("What is the body message?")
                body = input_fn("Body: ").strip()
            if not body:
                body = "This is a test email sent from the Python Voice Assistant."

        # Check mock / test mode
        if MOCK_EMAIL or not SMTP_USER or not SMTP_PASSWORD:
            print("\n📧 [SIMULATED EMAIL / TEST MODE]")
            print(f"To: {recipient}")
            print(f"Subject: {subject}")
            print(f"Body: {body}")
            print("Status: Successfully simulated via test/dummy SMTP handler.\n")
            msg = f"Email to {recipient} with subject '{subject}' has been sent successfully in test mode."
            self.tts.speak(msg)
            return msg

        # Real SMTP Delivery
        try:
            msg_obj = email.message.EmailMessage()
            msg_obj["From"] = SMTP_USER
            msg_obj["To"] = recipient
            msg_obj["Subject"] = subject
            msg_obj.set_content(body)

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg_obj)

            msg = f"Email successfully sent to {recipient}."
            self.tts.speak(msg)
            return msg
        except Exception as e:
            err_msg = f"Failed to send email via SMTP: {e}"
            print(f"[Email Error] {err_msg}")
            self.tts.speak("Sorry, there was an error sending the email. Please check your SMTP settings.")
            return err_msg

    def handle_qa(self, query: str) -> str:
        """Advanced Tier: Answer general knowledge questions using Wikipedia QA API."""
        clean_query = query.strip()
        if not clean_query:
            msg = "What question would you like to ask?"
            self.tts.speak(msg)
            return msg

        # Try Wikipedia REST API summary
        try:
            formatted_title = clean_query.replace(" ", "_")
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(formatted_title)}"
            res = requests.get(url, headers={"User-Agent": "VoiceAssistant/1.0"}, timeout=6)
            if res.status_code == 200:
                data = res.json()
                extract = data.get("extract")
                if extract:
                    # Limit to 2 sentences for pleasant speech readout
                    sentences = extract.split(". ")
                    short_summary = ". ".join(sentences[:2])
                    if not short_summary.endswith("."):
                        short_summary += "."
                    self.tts.speak(short_summary)
                    return short_summary

            # If direct title was not found, try search
            search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(clean_query)}&limit=1&format=json"
            search_res = requests.get(search_url, headers={"User-Agent": "VoiceAssistant/1.0"}, timeout=6)
            if search_res.status_code == 200:
                search_data = search_res.json()
                if len(search_data) >= 3 and search_data[2] and search_data[2][0]:
                    ans = search_data[2][0]
                    self.tts.speak(ans)
                    return ans
        except Exception as e:
            print(f"[QA] Wikipedia query error: {e}")

        # Fallback response
        msg = f"I couldn't find a direct answer for '{clean_query}'. Would you like me to search the web for it?"
        self.tts.speak(msg)
        return msg

    def handle_custom_command(self, trigger: str, response: str) -> str:
        """Execute a matched custom command."""
        output, _ = self.custom_mgr.execute_response(response)
        self.tts.speak(output)
        return output

    def handle_add_command(
        self,
        trigger: Optional[str] = None,
        response: Optional[str] = None,
        input_fn: Optional[Callable[[str], str]] = None,
    ) -> str:
        """Advanced Tier: Allow users to add custom commands via voice prompt or config file."""
        if not trigger:
            if input_fn:
                self.tts.speak("What phrase would you like to use to trigger the command?")
                trigger = input_fn("Trigger phrase: ").strip()

        if not response:
            if input_fn:
                self.tts.speak("What should I say or what website should I open when this command is called?")
                response = input_fn("Command response/URL: ").strip()

        if not trigger or not response:
            msg = "Could not add custom command because trigger or response was missing."
            self.tts.speak(msg)
            return msg

        ok = self.custom_mgr.add_command(trigger, response)
        if ok:
            msg = f"Custom command added successfully. When you say '{trigger}', I will respond with '{response}'."
        else:
            msg = "Failed to save custom command."
        self.tts.speak(msg)
        return msg

    def handle_list_commands(self) -> str:
        """List all available custom commands."""
        cmds = self.custom_mgr.commands
        if not cmds:
            msg = "There are currently no custom commands configured."
            self.tts.speak(msg)
            return msg

        print("\n📋 [CUSTOM COMMANDS]")
        for trigger, resp in cmds.items():
            print(f"  • '{trigger}' -> {resp}")
        print()

        triggers_list = ", ".join(cmds.keys())
        msg = f"You have {len(cmds)} custom commands configured: {triggers_list}"
        self.tts.speak(msg)
        return msg

    def handle_help(self) -> str:
        """Describe assistant capabilities."""
        help_text = (
            f"I am {ASSISTANT_NAME}. Here is what I can do for you:\n"
            "  • Greetings: Say 'Hello' or 'Hi'\n"
            "  • Time & Date: Ask 'What time is it?' or 'What is today's date?'\n"
            "  • Web Search: Say 'Search the web for Python programming'\n"
            "  • Live Weather: Ask 'What is the weather in Paris?'\n"
            "  • Timed Reminders: Say 'Remind me in 10 seconds to stretch'\n"
            "  • Send Email: Say 'Send an email'\n"
            "  • General Knowledge: Ask 'Who was Albert Einstein?' or 'What is quantum computing?'\n"
            "  • Custom Commands: Say 'Add custom command' or 'List custom commands'\n"
            "  • Exit: Say 'Goodbye' or 'Exit'\n"
        )
        print(f"\n{help_text}")
        speech_msg = (
            f"I can tell the time and date, search the web, report live weather, "
            f"set reminders with alerts, send emails, answer general knowledge questions, "
            f"and run custom commands."
        )
        self.tts.speak(speech_msg, print_text=False)
        return help_text
