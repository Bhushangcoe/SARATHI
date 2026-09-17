"""
SARATHI's conversational brain.

Loads a large, easily-expandable JSON file of patterns -> responses,
and matches user input against it two ways:
  1. Exact substring match (fast, precise)
  2. Fuzzy match via difflib (catches rephrasing, typos, near-misses)

To add more knowledge, just edit knowledge_base.json - no code changes
needed. No LLM, no internet, no dependencies beyond the standard library.
"""

import difflib
import json
import random
from pathlib import Path

_DATA_PATH = Path(__file__).resolve().parent / "knowledge_base.json"

FUZZY_CUTOFF = 0.72  # 0-1, higher = stricter match required


def _load_knowledge():
    try:
        with open(_DATA_PATH, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if not content:
            print(f"[SARATHI] Warning: {_DATA_PATH} is empty. Conversation data will not load.")
            return {}, {}

        data = json.loads(content)

    except FileNotFoundError:
        print(f"[SARATHI] Warning: {_DATA_PATH} not found. Conversation data will not load.")
        return {}, {}
    except json.JSONDecodeError as error:
        print(f"[SARATHI] Warning: {_DATA_PATH} has invalid JSON ({error}). Conversation data will not load.")
        return {}, {}

    pattern_to_tag = {}
    responses_by_tag = {}

    for intent in data.get("intents", []):
        tag = intent["tag"]
        responses_by_tag[tag] = intent["responses"]
        for pattern in intent["patterns"]:
            pattern_to_tag[pattern.lower()] = tag

    return pattern_to_tag, responses_by_tag


_PATTERN_TO_TAG, _RESPONSES_BY_TAG = _load_knowledge()
_ALL_PATTERNS = list(_PATTERN_TO_TAG.keys())


def get_reply(message):
    """Return a matched response, or None if nothing matched well enough."""
    message = message.lower().strip()
    if not message:
        return None

    # 1. Exact substring match - most reliable
    for pattern, tag in _PATTERN_TO_TAG.items():
        if pattern in message:
            return random.choice(_RESPONSES_BY_TAG[tag])

    # 2. Fuzzy match - catches rephrasing and small differences
    close_matches = difflib.get_close_matches(
        message, _ALL_PATTERNS, n=1, cutoff=FUZZY_CUTOFF
    )
    if close_matches:
        tag = _PATTERN_TO_TAG[close_matches[0]]
        return random.choice(_RESPONSES_BY_TAG[tag])

    return None