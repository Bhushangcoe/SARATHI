"""
SARATHI Brain
-------------
AI conversation engine for SARATHI.

Responsibilities:
1. Handle normal conversation.
2. Maintain short-term conversation memory.
3. Use local knowledge when appropriate.
4. Send unknown/general questions to Groq.
5. Produce natural, voice-friendly answers.
"""

import os
import re
from pathlib import Path

from groq import Groq


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "openai/gpt-oss-20b"

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_FILE = BASE_DIR / "knowledge_base.json"

MAX_HISTORY = 14

_client = None
_conversation_history = []


# ============================================================
# GROQ CLIENT
# ============================================================

def _get_client():
    global _client

    if _client is not None:
        return _client

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("[SARATHI] GROQ_API_KEY not found.")
        return None

    try:
        _client = Groq(api_key=api_key)
        print("[SARATHI] Groq API initialized successfully.")
        return _client

    except Exception as error:
        print(f"[SARATHI] Groq initialization failed: {error}")
        return None


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def _normalize(text):
    text = str(text or "").strip().lower()

    replacements = {
        "what's": "what is",
        "who's": "who is",
        "how's": "how is",
        "where's": "where is",
        "that's": "that is",
        "it's": "it is",
        "i'm": "i am",
        "you're": "you are",
        "we're": "we are",
        "don't": "do not",
        "can't": "cannot",
        "won't": "will not",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# KNOWLEDGE BASE
# ============================================================

def _load_knowledge_base():
    if not KNOWLEDGE_FILE.exists():
        return {}

    try:
        import json

        with open(
            KNOWLEDGE_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if isinstance(data, dict):
            return data

    except Exception as error:
        print(
            f"[SARATHI] Knowledge base error: {error}"
        )

    return {}


def _knowledge_answer(message):
    """
    Use only strong/exact knowledge-base matches.

    Deliberately avoids aggressive fuzzy matching because
    fuzzy matching previously caused unrelated answers.
    """

    knowledge = _load_knowledge_base()

    if not knowledge:
        return None

    normalized_message = _normalize(message)

    # --------------------------------------------------------
    # EXACT MATCH
    # --------------------------------------------------------

    for question, answer in knowledge.items():

        if not isinstance(question, str):
            continue

        if _normalize(question) == normalized_message:

            if isinstance(answer, str):
                return answer

    # --------------------------------------------------------
    # STRONG MULTI-WORD MATCH
    # --------------------------------------------------------

    for question, answer in knowledge.items():

        if not isinstance(question, str):
            continue

        normalized_question = _normalize(question)

        words = normalized_question.split()

        if len(words) < 2:
            continue

        if normalized_question in normalized_message:

            coverage = len(words) / max(
                len(normalized_message.split()),
                1
            )

            if coverage >= 0.55:

                if isinstance(answer, str):
                    return answer

    return None


# ============================================================
# SARATHI PERSONALITY
# ============================================================

SYSTEM_PROMPT = """
You are SARATHI, Bhushan's personal desktop AI assistant.

Your personality:
- Friendly
- Intelligent
- Calm
- Natural
- Slightly playful when appropriate
- Helpful
- Confident without pretending to know things
- Never robotic
- Never overly formal

You are speaking through a voice assistant, so your answers
must sound natural when spoken aloud.

IMPORTANT RESPONSE STYLE:

1. Speak naturally, like a helpful intelligent friend.
2. Keep simple questions short.
3. For casual conversation, be warm and conversational.
4. For technical questions, explain clearly and practically.
5. If the user asks for code, provide useful code and explain it.
6. Avoid unnecessary headings.
7. Avoid Markdown tables.
8. Avoid bullet-heavy responses unless they genuinely help.
9. Do not use emojis excessively.
10. Do not repeat the user's question unnecessarily.
11. Do not say "As an AI language model".
12. Do not claim to have abilities you don't have.
13. Never pretend that you executed a computer command.
14. Keep spoken answers reasonably concise.
15. If the user asks a complex question, give the answer in
    manageable sections.
16. If the user says "bro", you may naturally use "bro" too.
17. If the user makes a joke, respond naturally.
18. If the user's question is ambiguous, ask a short
    clarification instead of guessing wildly.

VOICE-FIRST RULE:

Your response will be converted into speech using Piper TTS.

Therefore:
- Prefer normal sentences.
- Avoid strange symbols.
- Avoid Markdown formatting.
- Avoid huge walls of text.
- Avoid tables.
- Avoid URLs unless absolutely necessary.
- Don't start every answer with "Sure".
- Don't sound like a generic customer-support bot.

PERSONALITY EXAMPLES:

User: How are you?
Good:
"I'm doing great, bro. Ready when you are."

User: What is Python?
Good:
"Python is a programming language known for being simple,
powerful, and beginner-friendly. It's widely used for web
development, automation, data science, and AI."

User: Who is the president of India?
Answer the actual question directly.

User: I'm tired.
Good:
"Then take it easy for a bit, bro. You don't have to force
everything at once."

User: What should I learn next?
Give practical advice based on the conversation.

Remember recent conversation context and use it naturally.
"""


# ============================================================
# MEMORY
# ============================================================

def clear_memory():
    """
    Clear SARATHI's current conversation memory.
    """

    global _conversation_history

    _conversation_history = []

    print("[SARATHI] Conversation memory cleared.")


def get_memory():
    """
    Return a copy of current conversation memory.
    """

    return list(_conversation_history)


def _add_message(role, content):

    _conversation_history.append({
        "role": role,
        "content": content
    })

    # Keep memory small enough for fast requests.
    if len(_conversation_history) > MAX_HISTORY:

        del _conversation_history[
            0:len(_conversation_history) - MAX_HISTORY
        ]


# ============================================================
# RESPONSE CLEANING
# ============================================================

def clean_response(text):

    if not text:
        return ""

    text = str(text)

    # Remove code fences.
    text = re.sub(
        r"```[\w-]*",
        "",
        text
    )

    text = text.replace("```", "")

    # Remove Markdown headings.
    text = re.sub(
        r"^\s*#{1,6}\s*",
        "",
        text,
        flags=re.MULTILINE
    )

    # Remove bold/italic markers.
    text = text.replace("**", "")
    text = text.replace("__", "")
    text = text.replace("*", "")
    text = text.replace("_", " ")

    # Convert bullets into natural sentences.
    text = re.sub(
        r"^\s*[-•]\s*",
        "",
        text,
        flags=re.MULTILINE
    )

    # Remove Markdown links but keep their text.
    text = re.sub(
        r"\[([^\]]+)\]\([^)]+\)",
        r"\1",
        text
    )

    # Remove excessive whitespace.
    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# GROQ RESPONSE
# ============================================================

def _ask_groq(message):

    client = _get_client()

    if client is None:
        return (
            "I can't reach my AI brain right now. "
            "Please check the Groq API connection."
        )

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    # Add recent memory.
    messages.extend(_conversation_history)

    messages.append({
        "role": "user",
        "content": message
    })

    try:

        print("[SARATHI] Asking Groq...")

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        answer = response.choices[0].message.content

        answer = clean_response(answer)

        if not answer:
            answer = (
                "I didn't get a useful answer from my AI brain."
            )

        return answer

    except Exception as error:

        print(
            f"[SARATHI] Groq request failed: {error}"
        )

        return (
            "I hit a problem while thinking. "
            "Give me another try."
        )


# ============================================================
# MAIN BRAIN FUNCTION
# ============================================================

def get_reply(message):

    message = str(message or "").strip()

    if not message:
        return "I didn't hear anything."

    # --------------------------------------------------------
    # LOCAL KNOWLEDGE
    # --------------------------------------------------------

    local_answer = _knowledge_answer(message)

    if local_answer:

        local_answer = clean_response(
            local_answer
        )

        _add_message(
            "user",
            message
        )

        _add_message(
            "assistant",
            local_answer
        )

        return local_answer

    # --------------------------------------------------------
    # GROQ
    # --------------------------------------------------------

    answer = _ask_groq(message)

    # Save conversation.
    _add_message(
        "user",
        message
    )

    _add_message(
        "assistant",
        answer
    )

    return answer