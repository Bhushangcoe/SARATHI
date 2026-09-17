"""
SARATHI's voice, powered by Piper TTS - runs fully offline on your PC.

IMPORTANT PERFORMANCE NOTE:
This version loads the Piper voice model ONCE into memory using Piper's
Python API, instead of launching a new "piper" process (and reloading
the model from disk) on every single speak() call.

Call preload_voices() once, early, in a background thread when the app
starts (see ui/app.py) so the model is already warmed up by the time
Sarathi needs to speak.
"""

import wave
from pathlib import Path

import pygame
from piper import PiperVoice

VOICES_DIR = Path(__file__).resolve().parent.parent / "voices"

ENGLISH_MODEL = VOICES_DIR / "en_US-hfc_female-medium.onnx"

OUTPUT_FILE = Path("sarathi_voice.wav")

_voice_cache = {}


def _load_voice(model_path):
    key = str(model_path)
    if key not in _voice_cache:
        _voice_cache[key] = PiperVoice.load(key)
    return _voice_cache[key]


def preload_voices():
    """
    Call this once, early, in a background thread at app startup.
    Warms up the English voice so the first speak() call is fast.
    """
    try:
        _load_voice(ENGLISH_MODEL)
    except Exception as error:
        print(f"[SARATHI] Could not preload voice model: {error}")


def _generate_audio(text):
    if not ENGLISH_MODEL.exists():
        raise FileNotFoundError(
            f"Voice model not found at {ENGLISH_MODEL}. "
            "Make sure both the .onnx and .onnx.json files are in the voices/ folder."
        )

    voice = _load_voice(ENGLISH_MODEL)

    with wave.open(str(OUTPUT_FILE), "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)


def _play_audio():
    pygame.mixer.init()
    pygame.mixer.music.load(str(OUTPUT_FILE))
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.unload()
    pygame.mixer.quit()


def stop_speaking():
    """Immediately stop whatever Sarathi is currently saying, if anything."""
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass


def speak(text):
    """Generate and play SARATHI's voice using local Piper TTS."""
    try:
        _generate_audio(text)
        _play_audio()
    except FileNotFoundError as error:
        print(f"[SARATHI] Voice model missing: {error}")
    except Exception as error:
        print(f"[SARATHI] Could not generate speech: {error}")