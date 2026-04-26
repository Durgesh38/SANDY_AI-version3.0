"""
SANDY AI - Voice Input Module
================================
Captures voice commands via microphone and converts speech to text.
Also provides optional text-to-speech (TTS) response output.

Install requirements:
    pip install SpeechRecognition pyttsx3
    pip install pyaudio          (Windows / macOS)
    # Linux: apt install portaudio19-dev -y && pip install pyaudio

Usage:
    from voice.voice_input import get_voice_input, speak, check_microphone

    result = get_voice_input()
    if result["success"]:
        print(result["text"])
"""

# ──────────────────────────────────────────────────────────────────────
#  VOICE INPUT  (Speech → Text)
# ──────────────────────────────────────────────────────────────────────

def get_voice_input(timeout: int = 5, phrase_limit: int = 10) -> dict:
    """
    Listen for a voice command from the default microphone.

    Parameters
    ----------
    timeout      : int  — seconds to wait for speech to begin
    phrase_limit : int  — max seconds for a single phrase

    Returns
    -------
    dict with keys:
        success (bool)  — True if speech was captured & recognized
        text    (str)   — transcribed text (empty on failure)
        engine  (str)   — 'google' | 'sphinx_offline'
        error   (str)   — error message on failure
    """
    try:
        import speech_recognition as sr
    except ImportError:
        return {
            "success": False,
            "text":    "",
            "engine":  "",
            "error":   (
                "SpeechRecognition not installed.\n"
                "Run: pip install SpeechRecognition pyaudio"
            ),
        }

    recognizer = sr.Recognizer()
    recognizer.energy_threshold        = 300   # microphone sensitivity
    recognizer.pause_threshold         = 0.8   # silence before phrase ends
    recognizer.dynamic_energy_threshold = True

    try:
        with sr.Microphone() as source:
            # Calibrate for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)

            # Listen
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_limit,
            )

        # ── Primary: Google Speech Recognition (online) ──────────────
        try:
            text = recognizer.recognize_google(audio)
            return {
                "success": True,
                "text":    text,
                "engine":  "google",
                "error":   "",
            }

        except sr.UnknownValueError:
            return {
                "success": False,
                "text":    "",
                "engine":  "google",
                "error":   "Could not understand audio. Please speak clearly.",
            }

        except sr.RequestError:
            # ── Fallback: CMU Sphinx (offline) ───────────────────────
            try:
                text = recognizer.recognize_sphinx(audio)
                return {
                    "success": True,
                    "text":    text,
                    "engine":  "sphinx_offline",
                    "error":   "",
                }
            except sr.UnknownValueError:
                return {
                    "success": False,
                    "text":    "",
                    "engine":  "sphinx_offline",
                    "error":   "Offline recognition failed. Check microphone.",
                }
            except Exception as e:
                return {
                    "success": False,
                    "text":    "",
                    "engine":  "sphinx_offline",
                    "error":   f"Sphinx error: {str(e)}",
                }

    except sr.WaitTimeoutError:
        return {
            "success": False,
            "text":    "",
            "engine":  "",
            "error":   f"No speech detected within {timeout} seconds.",
        }

    except OSError:
        return {
            "success": False,
            "text":    "",
            "engine":  "",
            "error":   (
                "No microphone found.\n"
                "Check that a microphone is connected and not muted."
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "text":    "",
            "engine":  "",
            "error":   f"Unexpected error: {str(e)}",
        }


# ──────────────────────────────────────────────────────────────────────
#  MICROPHONE CHECK
# ──────────────────────────────────────────────────────────────────────

def check_microphone() -> bool:
    """
    Return True if a working microphone is detected, False otherwise.
    """
    try:
        import speech_recognition as sr
        with sr.Microphone():
            return True
    except Exception:
        return False


# ──────────────────────────────────────────────────────────────────────
#  TEXT-TO-SPEECH  (optional SANDY voice responses)
# ──────────────────────────────────────────────────────────────────────

def speak(text: str, rate: int = 165, volume: float = 0.9) -> None:
    """
    Speak the given text aloud using the system TTS engine.

    Parameters
    ----------
    text   : str   — text to speak
    rate   : int   — words per minute (default 165)
    volume : float — 0.0 to 1.0 (default 0.9)

    Requires: pip install pyttsx3
    Silently skips if pyttsx3 is not installed.
    """
    try:
        import pyttsx3

        engine = pyttsx3.init()
        engine.setProperty("rate",   rate)
        engine.setProperty("volume", volume)

        # Try to use a female voice if available
        voices = engine.getProperty("voices")
        for voice in voices:
            if "female" in voice.name.lower() or "zira" in voice.name.lower():
                engine.setProperty("voice", voice.id)
                break

        engine.say(text)
        engine.runAndWait()
        engine.stop()

    except ImportError:
        pass   # pyttsx3 not installed — TTS is optional, skip silently

    except Exception:
        pass   # Any other TTS error — skip silently, don't crash SANDY


# ──────────────────────────────────────────────────────────────────────
#  QUICK TEST  (run this file directly to test your microphone)
# ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  SANDY AI — Voice Input Test")
    print("=" * 50)

    mic_ok = check_microphone()
    print(f"Microphone detected : {'✓ YES' if mic_ok else '✗ NO'}")

    if mic_ok:
        print("\nSpeak a command now (5 second window)...")
        result = get_voice_input(timeout=5, phrase_limit=10)

        if result["success"]:
            print(f"\n✓ Recognized [{result['engine']}]: \"{result['text']}\"")
            speak(f"I heard: {result['text']}")
        else:
            print(f"\n✗ Failed: {result['error']}")
    else:
        print("\nNo microphone found. Connect a mic and try again.")
