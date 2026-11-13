# 🎙️ Aura — Intelligent Python Voice Assistant

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A modular, extensible, and cross-platform desktop voice assistant built in Python. **Aura** combines speech recognition, text-to-speech synthesis, rule-based natural language understanding (NLU), live API integrations, email dispatching, non-blocking asynchronous timers, and persistent custom command management.

Whether you prefer hands-free voice control or keyboard-driven text interaction, Aura adapts dynamically to your hardware environment with automatic fallback modes.

---

## 🌟 Key Features

- **🎙️ Dual Input Modes (Voice & Text):**
  - **Speech-to-Text (STT):** Powered by `speech_recognition` and Google Web Speech API with automatic ambient noise calibration.
  - **Interactive Text Mode (`--text`):** Fully functional terminal chat interface when a microphone is unavailable or when working in quiet spaces.
  - **Automatic Hardware Fallback:** Seamlessly switches to text input if no active microphone or PyAudio driver is detected.

- **🔊 Natural Text-to-Speech (TTS):**
  - Offline multi-engine speech synthesis using `pyttsx3` (Windows SAPI5, macOS NSSpeechSynthesizer, Linux espeak).
  - Configurable speech rate, volume, and voice selection via `.env`.
  - **Mute Mode (`--mute`):** Silently outputs all assistant responses exclusively to the console.

- **🧠 Natural Language Understanding (NLU):**
  - Regex-powered tokenization and scoring engine with entity extraction.
  - Understands flexible conversational phrasing for greetings, time, date, searches, weather, reminders, emails, knowledge queries, and custom macros.

- **🌤️ Live Weather Forecasts:**
  - Real-time weather reporting via OpenWeatherMap API with temperature, weather condition, and humidity.
  - **Resilient Fallback:** Zero-config fallback to `wttr.in` JSON endpoint if no API key is provided.

- **⏰ Asynchronous Reminders:**
  - Non-blocking background reminder daemon using Python `threading`.
  - Auditory and visual chime alerts triggered precisely upon countdown expiration while the assistant continues listening.

- **📧 Secure Email Dispatcher:**
  - Standard library `smtplib` with STARTTLS encryption.
  - **Safe Simulation Mode (`MOCK_EMAIL=true`):** Enabled by default to test email formatting and parameters safely without sending actual messages.

- **🌐 Web Search & Knowledge QA:**
  - Direct web query launcher (opens search results in your default browser).
  - Wikipedia REST API integration for concise direct answers to factual queries.

- **🛠️ Persistent Custom Commands:**
  - Dynamic JSON-backed user command manager (`custom_commands.json`).
  - Add, list, and trigger custom responses and URL shortcuts on the fly with live hot-reloading.

- **🚀 Automated Feature Demonstration (`--demo`):**
  - End-to-end automated walkthrough testing every single capability in sequence without requiring voice or user typing.

---

## 📂 Project Architecture

```text
voice-assistant/
│
├── assistant/                      # Core Assistant Package
│   ├── __init__.py                 # Package initializer
│   ├── actions.py                  # Action execution handlers (weather, email, reminder, search, etc.)
│   ├── audio.py                    # C-level stderr audio stream suppression (cleans terminal output)
│   ├── config.py                   # Environment variable loader and configuration defaults
│   ├── custom_cmds.py              # Persistent JSON custom command storage manager
│   ├── nlu.py                      # Rule-based NLU engine, intent classification & entity extraction
│   └── speech.py                   # Speech recognition (STT) and voice synthesis (TTS) managers
│
├── tests/                          # Automated Unit Test Suite
│   ├── __init__.py
│   ├── test_actions.py             # Action handler and mock dispatch tests
│   ├── test_custom_cmds.py         # JSON storage, add, delete, and reload tests
│   └── test_nlu.py                 # NLU pattern matching and entity extraction tests
│
├── .env.example                    # Sample environment variables template
├── .gitignore                      # Git exclusion rules
├── custom_commands.json            # Persistent storage for user-defined custom macros
├── main.py                         # CLI entry point and interactive event loop
├── requirements.txt                # Production package dependencies
└── README.md                       # Comprehensive documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10, 3.11, or 3.12** installed and added to your system `PATH`.
- **Git** installed on your system.
- *(Optional)* Working microphone and audio speakers/headphones.

---

### 2. Clone and Navigate

```bash
git clone https://github.com/LAKSHYAMARODIA01/voice-assistant.git
cd voice-assistant
```

---

### 3. Create and Activate a Virtual Environment

#### On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### On Windows (Command Prompt):
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

#### On macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> [!TIP]
> **Windows PyAudio Installation:**
> On Windows with Python 3.10+, `pip install pyaudio` automatically fetches pre-compiled official binary wheels. If you encounter any compiler issues on other platforms, you can run in text mode anytime (`python main.py --text`) without requiring PyAudio!

---

### 5. Configure Environment Variables

Create your local `.env` configuration file from the template:

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Windows (Command Prompt)
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` in any text editor and adjust options as needed:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `ASSISTANT_NAME` | `Aura` | The name the assistant responds with. |
| `TTS_RATE` | `175` | Speech speed rate in words per minute (WPM). |
| `TTS_VOLUME` | `1.0` | Speech volume level between `0.0` (silent) and `1.0` (max). |
| `OPENWEATHER_API_KEY` | *(blank)* | Free API key from [OpenWeatherMap](https://openweathermap.org/api). Uses `wttr.in` fallback if blank. |
| `DEFAULT_CITY` | `New York` | Default location for weather reports when none is specified. |
| `MOCK_EMAIL` | `true` | When `true`, simulates email delivery safely in terminal without sending real emails. |
| `SMTP_SERVER` | `smtp.gmail.com` | SMTP host server for real email transmission. |
| `SMTP_PORT` | `587` | SMTP TLS port. |
| `SMTP_USER` | *(blank)* | Your email address or SMTP username. |
| `SMTP_PASSWORD` | *(blank)* | Your email app password (e.g., Google App Password). |
| `DEFAULT_RECIPIENT` | `user@example.com` | Fallback recipient address. |

---

## 💻 Running the Assistant

### Mode A: Interactive Voice Mode (Default)
Speak commands naturally into your microphone:
```bash
python main.py
```

### Mode B: Interactive Text Mode (Recommended for testing / quiet environments)
Type queries directly into the terminal while still receiving voice feedback:
```bash
python main.py --text
```

### Mode C: Silent / Muted Mode
Disables all voice audio output; responses are displayed strictly on screen:
```bash
python main.py --text --mute
```

### Mode D: Automated End-to-End Demo
Executes a scripted demonstration of every capability (NLU, Time, Weather, Mock Email, Reminders, Custom Commands):
```bash
python main.py --demo
```

---

## 🗣️ Supported Commands & Voice Queries

| Category | Example Voice / Text Queries | Description |
| :--- | :--- | :--- |
| **Greetings** | *"Hello"*, *"Good morning"*, *"How are you?"* | Conversational greeting and status check. |
| **Time & Date** | *"What time is it?"*, *"What is today's date?"*, *"Date and time"* | Live system clock and calendar lookup. |
| **Web Search** | *"Search for quantum computing"*, *"Google Alan Turing"* | Opens your web browser with the search results. |
| **Knowledge QA** | *"Who was Ada Lovelace?"*, *"What is Python programming language?"* | Concise Wikipedia summary extraction. |
| **Weather** | *"What's the weather in London?"*, *"Weather report"* | Current temperature, conditions, and humidity. |
| **Reminders** | *"Remind me in 30 seconds to check the oven"* | Asynchronous countdown alert in the background. |
| **Email Dispatch** | *"Send an email to user@example.com with subject Meeting and body Hello"* | Sends an email (simulated by default for safety). |
| **Custom Commands** | *"Tell me a joke"*, *"Open github"*, *"List custom commands"* | User-configured responses and shortcuts. |
| **Add Custom Command** | *"Add custom command"* | Interactive wizard to define new custom voice triggers. |
| **Help & Exit** | *"Help"*, *"What can you do?"*, *"Goodbye"*, *"Exit"* | Shows available commands or terminates session. |

---

## 🛠️ Custom Command Customization

Aura supports persistent custom commands stored in `custom_commands.json`. You can add commands programmatically, verbally, or by directly editing `custom_commands.json`:

```json
{
  "tell me a joke": "Why do programmers prefer dark mode? Because light attracts bugs!",
  "who made you": "I was built as a Python Voice Assistant with speech recognition and natural language processing.",
  "what is your name": "My name is Aura, your personal Python voice assistant.",
  "open github": "https://github.com",
  "quote": "The only way to do great work is to love what you do. — Steve Jobs"
}
```

- If the response value begins with `http://` or `https://`, Aura automatically opens the URL in your default browser.
- Otherwise, Aura speaks and prints the custom response text.

---

## 🧪 Running Automated Unit Tests

A comprehensive unit test suite is included in the `tests/` directory covering actions, custom command persistence, and the NLU parsing engine:

```bash
python -m unittest discover tests -v
```

All 21 test cases execute cleanly and mock external network/hardware dependencies.

---

## 🔧 Troubleshooting Guide

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `No module named 'speech_recognition'` | Dependencies not installed in active environment | Activate your virtual environment and run `pip install -r requirements.txt`. |
| `PyAudio compilation error on pip install` | Missing C++ build tools on host system | PyAudio wheels are available for Python 3.10-3.12 on Windows. On Linux: `sudo apt-get install python3-pyaudio portaudio19-dev`. Alternatively, run with `--text` mode which requires no audio input libraries. |
| `Microphone not capturing speech` | Microphone permissions or wrong default device | Verify microphone privacy settings in Windows Settings > Privacy > Microphone. |
| `Email authentication failed` | Gmail blocks plain passwords | Use a generated Google App Password (2-Step Verification > App Passwords) rather than your personal account password, or keep `MOCK_EMAIL=true`. |
| `wttr.in timeout or weather error` | Network restrictions or proxy blocking outgoing HTTP | Provide a free `OPENWEATHER_API_KEY` in `.env` for direct authenticated REST calls. |

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) — feel free to use, modify, and distribute.
