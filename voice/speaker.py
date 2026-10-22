"""
SARATHI Voice Speaker
---------------------

Piper TTS voice output.

Features:
- English Piper voice
- Voice caching
- Markdown cleanup
- Natural speech pacing
- Spacebar interruption support
"""

import re
import threading
import wave
from pathlib import Path

import pygame
from piper import PiperVoice


# ============================================================
# PATHS
# ============================================================

VOICES_DIR = (
    Path(__file__).resolve().parent.parent / "voices"
)

ENGLISH_MODEL = (
    VOICES_DIR /
    "en_US-hfc_female-medium.onnx"
)

OUTPUT_FILE = (
    Path(__file__).resolve().parent /
    "sarathi_voice.wav"
)


# ============================================================
# SETTINGS
# ============================================================

# Slightly slower than default.
SPEECH_LENGTH_SCALE = 1.18

_voice_cache = {}

_speech_lock = threading.Lock()


# ============================================================
# VOICE LOADING
# ============================================================

def _load_voice(model_path):

    key = str(model_path)

    if key not in _voice_cache:

        print(
            f"[SARATHI] Loading Piper voice..."
        )

        _voice_cache[key] = PiperVoice.load(
            key
        )

        print(
            "[SARATHI] Piper voice loaded."
        )

    return _voice_cache[key]


def preload_voices():

    try:

        _load_voice(
            ENGLISH_MODEL
        )

    except Exception as error:

        print(
            "[SARATHI] Could not preload voice "
            f"model: {error}"
        )


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_for_speech(text):

    if not text:
        return ""

    text = str(text)

    # Remove code blocks.
    text = re.sub(
        r"```[\s\S]*?```",
        "",
        text
    )

    # Remove Markdown headings.
    text = re.sub(
        r"^\s*#{1,6}\s*",
        "",
        text,
        flags=re.MULTILINE
    )

    # Remove bold / italic formatting.
    text = text.replace("**", "")
    text = text.replace("__", "")
    text = text.replace("*", "")
    text = text.replace("_", " ")

    # Remove Markdown links but preserve visible text.
    text = re.sub(
        r"\[([^\]]+)\]\([^)]+\)",
        r"\1",
        text
    )

    # Remove URLs.
    text = re.sub(
        r"https?://\S+",
        "",
        text
    )

    # Convert common bullets.
    text = re.sub(
        r"^\s*[-•]\s*",
        "",
        text,
        flags=re.MULTILINE
    )

    # Remove table separators.
    text = re.sub(
        r"^\s*\|?[\s|:-]+\|?\s*$",
        "",
        text,
        flags=re.MULTILINE
    )

    # Remove pipe table formatting.
    text = text.replace("|", ", ")

    # Remove weird repeated symbols.
    text = re.sub(
        r"[`~^]+",
        "",
        text
    )

    # Keep normal punctuation.
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    # Limit excessive blank lines.
    text = re.sub(
        r"\n{2,}",
        ". ",
        text
    )

    # Clean spaces before punctuation.
    text = re.sub(
        r"\s+([,.!?])",
        r"\1",
        text
    )

    return text.strip()


# ============================================================
# AUDIO GENERATION
# ============================================================

def _generate_audio(text):

    if not ENGLISH_MODEL.exists():

        raise FileNotFoundError(
            f"Voice model not found at "
            f"{ENGLISH_MODEL}. "
            f"Make sure both the .onnx and "
            f".onnx.json files exist."
        )

    voice = _load_voice(
        ENGLISH_MODEL
    )

    with wave.open(
        str(OUTPUT_FILE),
        "wb"
    ) as wav_file:

        try:

            voice.synthesize_wav(
                text,
                wav_file,
                length_scale=SPEECH_LENGTH_SCALE
            )

        except TypeError:

            voice.synthesize_wav(
                text,
                wav_file
            )


# ============================================================
# AUDIO PLAYBACK
# ============================================================

def _play_audio():

    try:

        if not pygame.mixer.get_init():

            pygame.mixer.init(
                frequency=22050,
                size=-16,
                channels=1,
                buffer=512
            )

            print(
                "[SARATHI] Audio system initialized."
            )

        pygame.mixer.music.load(
            str(OUTPUT_FILE)
        )

        pygame.mixer.music.play()

        clock = pygame.time.Clock()

        while pygame.mixer.music.get_busy():

            clock.tick(20)

    finally:

        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        except Exception:
            pass


# ============================================================
# STOP SPEAKING
# ============================================================

def stop_speaking():

    try:

        if pygame.mixer.get_init():

            pygame.mixer.music.stop()

    except Exception:
        pass


# ============================================================
# SPEAK
# ============================================================

def speak(text):

    cleaned_text = clean_for_speech(
        text
    )

    if not cleaned_text:
        return

    # Prevent overlapping TTS calls.
    with _speech_lock:

        try:

            print(
                f"SARATHI [TTS]: {cleaned_text}"
            )

            _generate_audio(
                cleaned_text
            )

            _play_audio()

        except FileNotFoundError as error:

            print(
                f"[SARATHI] Voice model missing: "
                f"{error}"
            )

        except Exception as error:

            print(
                f"[SARATHI] Could not generate "
                f"speech: {error}"
            )