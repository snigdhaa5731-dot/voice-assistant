"""
Main entry point for the Python Voice Assistant.
Implements the continuous interactive loop with both Voice and Text modes.
"""

import argparse
import sys
import time

from assistant.actions import ActionHandler
from assistant.config import ASSISTANT_NAME
from assistant.custom_cmds import CustomCommandManager
from assistant.nlu import IntentType, NLUEngine
from assistant.speech import STTManager, TTSManager


BANNER = f"""
=============================================================
             🎙️  {ASSISTANT_NAME.upper()} - PYTHON VOICE ASSISTANT  🎙️
   Beginner & Advanced Tier: Speech, NLU, Weather, Reminders,
               Email (smtplib) & Custom Commands
=============================================================
"""


def parse_args():
    parser = argparse.ArgumentParser(description=f"{ASSISTANT_NAME} - Python Voice Assistant")
    parser.add_argument(
        "--text",
        action="store_true",
        help="Run in interactive text mode (type commands instead of speaking)",
    )
    parser.add_argument(
        "--mute",
        action="store_true",
        help="Mute text-to-speech voice output (display responses in terminal only)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run an automated end-to-end demonstration of all assistant features",
    )
    return parser.parse_args()


def run_demo(action_handler: ActionHandler, nlu: NLUEngine):
    """Run an automated demonstration of all features."""
    print("\n🚀 [STARTING AUTOMATED FEATURE DEMONSTRATION]\n")

    demo_commands = [
        ("Beginner: Greeting", "Hello"),
        ("Beginner: Current Time", "What time is it?"),
        ("Beginner: Current Date", "What is today's date?"),
        ("Beginner: Web Search", "Search for Alan Turing"),
        ("Advanced: General Knowledge QA", "Who was Ada Lovelace?"),
        ("Advanced: Live Weather", "What is the weather in London?"),
        ("Advanced: Timed Reminder", "Remind me in 3 seconds to take a deep breath"),
        ("Advanced: Send Email (Mock)", "Send an email to rahul@example.com with subject Project Demo and body Voice assistant test passed"),
        ("Advanced: List Custom Commands", "List custom commands"),
        ("Advanced: Trigger Custom Command", "Tell me a joke"),
        ("Beginner/Advanced: Exit", "Goodbye"),
    ]

    for label, cmd_text in demo_commands:
        print(f"\n👉 [{label}]")
        print(f"User Utterance: \"{cmd_text}\"")
        intent_res = nlu.parse(cmd_text)
        print(f"Parsed Intent: {intent_res.intent.name} (Entities: {intent_res.entities})")
        execute_intent(intent_res, action_handler, nlu, input_provider=lambda prompt: "demo_val")
        time.sleep(1.5)

    print("\n✅ [DEMONSTRATION COMPLETED SUCCESSFULLY]\n")


def execute_intent(intent_res, action_handler: ActionHandler, nlu: NLUEngine, input_provider=input) -> bool:
    """
    Execute actions based on parsed intent.
    Returns True to continue, False to exit.
    """
    intent = intent_res.intent
    entities = intent_res.entities
    raw = intent_res.raw_text

    if intent == IntentType.EXIT:
        action_handler.tts.speak(f"Goodbye! Have a wonderful day from {ASSISTANT_NAME}.")
        return False

    elif intent == IntentType.GREETING:
        action_handler.handle_greeting()

    elif intent == IntentType.TIME:
        action_handler.handle_time()

    elif intent == IntentType.DATE:
        action_handler.handle_date()

    elif intent == IntentType.DATETIME:
        action_handler.handle_datetime()

    elif intent == IntentType.WEB_SEARCH:
        query = entities.get("query", raw)
        action_handler.handle_web_search(query)

    elif intent == IntentType.WEATHER:
        city = entities.get("city")
        action_handler.handle_weather(city)

    elif intent == IntentType.REMINDER:
        duration = entities.get("duration", 0)
        message = entities.get("message", "Reminder alert!")
        if duration == 0:
            action_handler.tts.speak("For how many seconds should I set the reminder?")
            try:
                ans = input_provider("Reminder duration (seconds): ")
                duration = int("".join(filter(str.isdigit, ans)) or "10")
            except Exception:
                duration = 10
        action_handler.handle_reminder(duration, message)

    elif intent == IntentType.EMAIL:
        action_handler.handle_email(
            recipient=entities.get("recipient"),
            subject=entities.get("subject"),
            body=entities.get("body"),
            input_fn=input_provider,
        )

    elif intent == IntentType.QA:
        query = entities.get("query", raw)
        action_handler.handle_qa(query)

    elif intent == IntentType.ADD_COMMAND:
        action_handler.handle_add_command(
            trigger=entities.get("trigger"),
            response=entities.get("response"),
            input_fn=input_provider,
        )

    elif intent == IntentType.LIST_COMMANDS:
        action_handler.handle_list_commands()

    elif intent == IntentType.CUSTOM_COMMAND:
        action_handler.handle_custom_command(
            trigger=entities.get("trigger", ""),
            response=entities.get("response", ""),
        )

    elif intent == IntentType.HELP:
        action_handler.handle_help()

    else:
        # Unknown intent
        action_handler.tts.speak(
            f"I didn't quite understand that command. You can say 'help' to hear what I can do, or ask me to search the web."
        )

    return True


def main():
    args = parse_args()
    print(BANNER)

    custom_mgr = CustomCommandManager()
    nlu = NLUEngine(custom_command_manager=custom_mgr)
    tts = TTSManager(muted=args.mute)
    action_handler = ActionHandler(tts=tts, custom_mgr=custom_mgr)

    if args.demo:
        run_demo(action_handler, nlu)
        return

    # Check mode
    if args.text:
        run_text_mode(action_handler, nlu)
    else:
        stt = STTManager()
        if not stt.is_microphone_available():
            print("\n⚠️  No active microphone detected. Automatically falling back to interactive text mode.\n")
            run_text_mode(action_handler, nlu)
        else:
            run_voice_mode(action_handler, nlu, stt)


def run_text_mode(action_handler: ActionHandler, nlu: NLUEngine):
    """Interactive text input loop with pyttsx3 speech responses."""
    print("💬 [TEXT MODE ACTIVATED]")
    print("Type your commands below (e.g. 'hello', 'what time is it', 'weather in Tokyo', 'help', 'exit').\n")

    while True:
        try:
            user_input = input("You > ").strip()
            if not user_input:
                continue

            intent_res = nlu.parse(user_input)
            should_continue = execute_intent(intent_res, action_handler, nlu, input_provider=input)
            if not should_continue:
                break
        except (KeyboardInterrupt, EOFError):
            print("\nExiting voice assistant. Goodbye!")
            break


def run_voice_mode(action_handler: ActionHandler, nlu: NLUEngine, stt: STTManager):
    """Full voice input and output loop with speech recognition and pyttsx3."""
    print("🎙️  [VOICE MODE ACTIVATED]")
    print("Speak clearly into your microphone. Say 'help' for options or 'goodbye' to exit.")
    print("Press Ctrl+C at any time to exit.\n")

    action_handler.handle_greeting()

    consecutive_errors = 0

    while True:
        try:
            transcript, error = stt.listen(timeout=6.0, phrase_time_limit=10.0)

            if error == "timeout":
                # User paused or didn't speak within timeout, loop quietly
                continue

            if error == "unrecognized":
                # Feature checklist: Graceful error handling: ask the user to repeat
                consecutive_errors += 1
                if consecutive_errors <= 2:
                    action_handler.tts.speak("I'm sorry, I didn't catch that. Could you please repeat?")
                else:
                    action_handler.tts.speak("I'm having trouble hearing you. You can speak louder or switch to text mode using --text.")
                    consecutive_errors = 0
                continue

            if error and error.startswith("network_error"):
                action_handler.tts.speak("I'm unable to connect to the speech recognition service. Please check your internet connection.")
                continue

            if error:
                print(f"[Audio Error] {error}")
                time.sleep(1)
                continue

            consecutive_errors = 0
            print(f"\n🗣️  You said: \"{transcript}\"")

            intent_res = nlu.parse(transcript)
            print(f"🎯 Recognized Intent: {intent_res.intent.name}")

            # Define voice input provider for interactive sub-prompts
            def voice_input_provider(prompt: str) -> str:
                print(prompt)
                sub_text, sub_err = stt.listen(timeout=5.0, phrase_time_limit=8.0)
                return sub_text if sub_text else ""

            should_continue = execute_intent(intent_res, action_handler, nlu, input_provider=voice_input_provider)
            if not should_continue:
                break

        except KeyboardInterrupt:
            print("\nShutting down voice assistant. Goodbye!")
            break
        except Exception as e:
            print(f"[Unexpected error] {e}")


if __name__ == "__main__":
    main()
