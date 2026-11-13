"""
Speech module: Text-to-Speech (pyttsx3) and Speech-to-Text (speech_recognition).
"""

import sys
import threading
from typing import Optional, Tuple
import pyttsx3
import speech_recognition as sr

from .audio import suppress_c_stderr
from .config import TTS_RATE, TTS_VOLUME, ASSISTANT_NAME


class TTSManager:
    """Manages Text-To-Speech output using pyttsx3."""

    def __init__(self, rate: int = TTS_RATE, volume: float = TTS_VOLUME, muted: bool = False):
        self.rate = rate
        self.volume = volume
        self.muted = muted
        self._lock = threading.Lock()
        self._engine = None
        self._init_engine()

    def _init_engine(self):
        try:
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self.rate)
            self._engine.setProperty("volume", self.volume)
        except Exception as e:
            print(f"[Warning] Could not initialize pyttsx3 engine: {e}", file=sys.stderr)
            self._engine = None

    def speak(self, text: str, print_text: bool = True) -> None:
        """Speak the given text and optionally print it to stdout."""
        if print_text:
            print(f"\n🤖 {ASSISTANT_NAME}: {text}\n")

        if self.muted or not self._engine:
            return

        with self._lock:
            try:
                # pyttsx3 sometimes needs fresh engine loop on Linux espeak
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception as e:
                # If engine hung or failed, try re-initializing
                try:
                    self._init_engine()
                    if self._engine:
                        self._engine.say(text)
                        self._engine.runAndWait()
                except Exception:
                    pass


class STTManager:
    """Manages Speech-To-Text input using speech_recognition."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.8
        self.recognizer.dynamic_energy_threshold = True
        self._calibrated = False

    def is_microphone_available(self) -> bool:
        """Check if any microphone device is accessible."""
        with suppress_c_stderr():
            try:
                mics = sr.Microphone.list_microphone_names()
                return len(mics) > 0
            except Exception:
                return False

    def calibrate(self, mic: sr.Microphone, duration: float = 0.8):
        """Calibrate microphone for ambient noise."""
        if not self._calibrated:
            try:
                print("🎙️  Calibrating for ambient background noise...")
                with suppress_c_stderr():
                    self.recognizer.adjust_for_ambient_noise(mic, duration=duration)
                self._calibrated = True
            except Exception:
                pass

    def listen(self, timeout: float = 5.0, phrase_time_limit: float = 8.0) -> Tuple[Optional[str], Optional[str]]:
        """
        Listen to microphone and recognize speech.
        Returns:
            (transcript, None) on success
            (None, error_type) on failure ('timeout', 'unrecognized', 'network_error', 'no_mic')
        """
        with suppress_c_stderr():
            try:
                with sr.Microphone() as source:
                    self.calibrate(source, duration=0.6)
                    print("🎧 Listening... (Speak now)")
                    audio = self.recognizer.listen(
                        source,
                        timeout=timeout,
                        phrase_time_limit=phrase_time_limit,
                    )
            except sr.WaitTimeoutError:
                return None, "timeout"
            except Exception as e:
                return None, f"no_mic: {e}"

        try:
            print("⏳ Processing speech...")
            text = self.recognizer.recognize_google(audio)
            return text, None
        except sr.UnknownValueError:
            return None, "unrecognized"
        except sr.RequestError as e:
            return None, f"network_error: {e}"
        except Exception as e:
            return None, f"error: {e}"
