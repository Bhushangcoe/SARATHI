"""
SARATHI core assistant brain.

Deterministic PC-control commands are checked first and handled by
system_actions.py.

Everything else is routed to the local Ollama model.

Features:
- YouTube search
- YouTube playback
- Google search
- Open websites
- Open folders
- Write notes
- Internet check
- Disk-space check
- DNS flush
- Temporary-file cleanup
- Recycle Bin
- PC checkup
- Close applications
- Open applications
- Notepad
- Calculator
- Gmail
- Word
- Excel
- PowerPoint
- Paint
- Task Manager
- Control Panel
- Settings
- Command Prompt
- Snipping Tool
- Lock PC
- Shutdown
- Restart
- Cancel shutdown
- Screenshot
- Coin flip
- Dice roll
- Current time
- Current date
- Local Ollama AI conversation

Language:
- Hinglish (Hindi + English mix), matching what the person speaks
"""


# ============================================================
# IMPORTS
# ============================================================

import subprocess
import webbrowser
from datetime import datetime

import requests

from core import system_actions


# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/chat"

OLLAMA_MODEL = "llama3.2"

REQUEST_TIMEOUT = 30


# ============================================================
# SARATHI SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = (
    "You are Sarathi, a helpful personal AI assistant. "

    "Always reply in English. "
    "Never reply in Hindi. "
    "Never reply in Hinglish. "
    "Never switch languages. "

    "Speak naturally like a friendly personal assistant. "

    "Keep responses short and natural, ideally one or two sentences, "
    "because your response will be spoken aloud through text-to-speech. "

    "Do not use markdown. "
    "Do not use bullet points. "
    "Do not use emojis. "

    "Be helpful, calm, friendly, and conversational."
)


# ============================================================
# CONVERSATION MEMORY
# ============================================================

_conversation_history = []

MAX_HISTORY_MESSAGES = 12


# ============================================================
# ASK OLLAMA
# ============================================================

def _ask_ollama(user_message):
    """
    Send the user's message to the local Ollama model.

    SARATHI replies in Hinglish, matching the person's language.
    """

    _conversation_history.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ] + _conversation_history[-MAX_HISTORY_MESSAGES:]

    try:

        response = requests.post(
            OLLAMA_URL,

            json={
                "model": OLLAMA_MODEL,

                "messages": messages,

                "stream": False,

                "keep_alive": "30m",

                "options": {
                    "num_predict": 80,
                },
            },

            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        reply = (
            data
            .get("message", {})
            .get("content", "")
            .strip()
        )

        if not reply:

            return (
                "I heard you, but I could not think "
                "of a reply just now."
            )

        _conversation_history.append(
            {
                "role": "assistant",
                "content": reply,
            }
        )

        return reply

    except requests.exceptions.ConnectionError:

        return (
            "I cannot reach my thinking engine right now. "
            "Please make sure Ollama is running."
        )

    except requests.exceptions.Timeout:

        return (
            "That took too long to think through. "
            "Could you try again?"
        )

    except requests.exceptions.RequestException:

        return (
            "Something went wrong while I was thinking. "
            "Please try again."
        )


# ============================================================
# COMMAND HANDLER
# ============================================================

def _handle_commands(message):
    """
    Handle deterministic computer commands.

    These commands are handled directly instead of being
    sent to Ollama.
    """

    # --------------------------------------------------------
    # YOUTUBE SEARCH
    # --------------------------------------------------------

    if (
        "search youtube for" in message
        or "youtube search for" in message
    ):

        query = message.split(
            "for",
            1
        )[1].strip()

        return system_actions.search_youtube(query)


    if (
        message.startswith("search youtube ")
        or message.startswith("youtube search ")
    ):

        query = message.split(
            " ",
            2
        )[2].strip()

        return system_actions.search_youtube(query)


    # --------------------------------------------------------
    # PLAY YOUTUBE VIDEO
    # --------------------------------------------------------

    if (
        message.startswith("play ")
        and "youtube" in message
    ):

        query = message.replace(
            "play ",
            "",
            1
        )

        query = query.replace(
            "on youtube",
            ""
        )

        query = query.replace(
            "youtube",
            ""
        )

        query = query.strip()

        return system_actions.play_youtube_video(query)


    if message.startswith("play "):

        query = message.replace(
            "play ",
            "",
            1
        ).strip()

        return system_actions.play_youtube_video(query)


    # --------------------------------------------------------
    # GOOGLE SEARCH
    # --------------------------------------------------------

    if message.startswith("search for "):

        query = message.replace(
            "search for ",
            "",
            1
        ).strip()

        return system_actions.search_google(query)


    if message.startswith("search "):

        query = message.replace(
            "search ",
            "",
            1
        ).strip()

        return system_actions.search_google(query)


    # --------------------------------------------------------
    # OPEN GOOGLE
    # --------------------------------------------------------

    if (
        "google" in message
        and any(
            phrase in message
            for phrase in [
                "open",
                "go to",
            ]
        )
    ):

        webbrowser.open(
            "https://www.google.com"
        )

        return "Opening Google for you."


    # --------------------------------------------------------
    # OPEN YOUTUBE
    # --------------------------------------------------------

    if (
        "youtube" in message
        and any(
            phrase in message
            for phrase in [
                "open",
                "go to",
            ]
        )
        and "search" not in message
    ):

        webbrowser.open(
            "https://www.youtube.com"
        )

        return "Kya dekhna chahte ho aap?"


    # --------------------------------------------------------
    # OPEN BROWSER
    # --------------------------------------------------------

    if any(
        phrase in message
        for phrase in [
            "open browser",
            "open my browser",
            "launch browser",
        ]
    ):

        return system_actions.open_browser()


    # --------------------------------------------------------
    # OPEN COMMON FOLDERS
    # --------------------------------------------------------

    for folder_name in [
        "documents",
        "downloads",
        "desktop",
        "pictures",
        "music",
        "videos",
    ]:

        if f"open {folder_name}" in message:

            return system_actions.open_folder(
                folder_name
            )


    # --------------------------------------------------------
    # OPEN THIS PC / FILE EXPLORER
    # --------------------------------------------------------

    if any(
        phrase in message
        for phrase in [
            "open this pc",
            "open my computer",
            "open file explorer",
            "open explorer",
        ]
    ):

        return system_actions.open_folder(
            "this pc"
        )


    # --------------------------------------------------------
    # WRITE A NOTE
    # --------------------------------------------------------

    if (
        message.startswith("write a note")
        or message.startswith("take a note")
        or message.startswith("make a note")
    ):

        for splitter in [
            "that",
            "saying",
            ":",
        ]:

            if splitter in message:

                text = message.split(
                    splitter,
                    1
                )[1].strip()

                return system_actions.write_note(
                    text
                )

        return (
            "What would you like me to write down?"
        )


    # --------------------------------------------------------
    # CHECK INTERNET
    # --------------------------------------------------------

    if any(
        phrase in message
        for phrase in [
            "check my internet",
            "is my internet working",
            "check internet connection",
        ]
    ):

        return system_actions.check_internet()


    # --------------------------------------------------------
    # CHECK DISK SPACE
    # --------------------------------------------------------

    if any(
        phrase in message
        for phrase in [
            "check disk space",
            "how much space do i have",
            "check storage",
        ]
    ):

        return system_actions.check_disk_space()


    # --------------------------------------------------------
    # FLUSH DNS
    # --------------------------------------------------------

    if any(
        phrase in message
        for phrase in [
            "flush dns",
            "fix my dns",
            "reset dns",
        ]
    ):

        return system_actions.flush_dns()


    # --------------------------------------------------------
    # CLEAR TEMP FILES
    # --------------------------------------------------------

    if any(
        phrase in message
        for phrase in [
            "clear temp files",
            "clean temp files",
            "clear temporary files",
        ]
    ):

        return system_actions.clear_temp_files()


    # --------------------------------------------------------
    # EMPTY RECYCLE BIN
    # --------------------------------------------------------

    if any(
        phrase in message
        for phrase in [
            "empty recycle bin",
            "empty the recycle bin",
            "empty trash",
        ]
    ):

        return system_actions.empty_recycle_bin()


    # --------------------------------------------------------
    # CURRENT WORLD CONFLICTS
    # --------------------------------------------------------

    if any(
        phrase in message
        for phrase in [
            "ongoing conflicts",
            "current conflicts",
            "world conflicts",
            "wars going on",
            "current wars",
            "what wars are happening",
        ]
    ):

        return system_actions.search_google(
            "current ongoing conflicts in the world"
        )


    # --------------------------------------------------------
    # PC CHECKUP
    # --------------------------------------------------------

    if any(
        phrase in message
        for phrase in [
            "check my pc",
            "find problems",
            "run a checkup",
            "fix my computer",
            "check my computer",
        ]
    ):

        return system_actions.run_quick_checkup()


    # --------------------------------------------------------
    # CLOSE APPLICATION
    # --------------------------------------------------------

    if (
        message.startswith("close ")
        or message.startswith("quit ")
        or message.startswith("exit ")
    ):

        app_name = ""

        for word in [
            "close ",
            "quit ",
            "exit ",
        ]:

            if message.startswith(word):

                app_name = message.replace(
                    word,
                    "",
                    1
                )

                break

        app_name = app_name.replace(
            "the ",
            ""
        )

        app_name = app_name.replace(
            "my ",
            ""
        )

        app_name = app_name.strip()

        return system_actions.close_app(
            app_name
        )


    # --------------------------------------------------------
    # OPEN NOTEPAD
    # --------------------------------------------------------

    if any(
        phrase in message
        for phrase in [
            "open notepad",
            "launch notepad",
            "start notepad",
        ]
    ):

        subprocess.Popen(
            ["notepad.exe"]
        )

        return "Opening Notepad for you."


    # --------------------------------------------------------
    # OPEN CALCULATOR
    # --------------------------------------------------------

    if any(
        phrase in message
        for phrase in [
            "open calculator",
            "launch calculator",
            "open calc",
        ]
    ):

        subprocess.Popen(
            ["calc.exe"]
        )

        return "Opening Calculator for you."


    # --------------------------------------------------------
    # OPEN GMAIL
    # --------------------------------------------------------

    if any(
        phrase in message
        for phrase in [
            "open gmail",
            "open email",
            "check my email",
        ]
    ):

        webbrowser.open(
            "https://mail.google.com"
        )

        return "Opening Gmail for you."


    # --------------------------------------------------------
    # OPEN MICROSOFT / WINDOWS APPLICATIONS
    # --------------------------------------------------------

    for app_name in [
        "word",
        "excel",
        "powerpoint",
        "paint",
        "task manager",
        "control panel",
        "settings",
        "command prompt",
        "snipping tool",
    ]:

        if f"open {app_name}" in message:

            return system_actions.open_app(
                app_name
            )


    # --------------------------------------------------------
    # LOCK PC
    # --------------------------------------------------------

    if any(
        phrase in message
        for phrase in [
            "lock my pc",
            "lock the pc",
            "lock my computer",
            "lock computer",
        ]
    ):

        return system_actions.lock_pc()


    # --------------------------------------------------------
    # CANCEL SHUTDOWN
    # --------------------------------------------------------

    if "cancel shutdown" in message:

        return system_actions.cancel_shutdown()


    # --------------------------------------------------------
    # SHUT DOWN PC
    # --------------------------------------------------------

    if any(
        phrase in message
        for phrase in [
            "shut down my pc",
            "shutdown my pc",
            "shut down the computer",
            "turn off my pc",
        ]
    ):

        return system_actions.shutdown_pc()


    # --------------------------------------------------------
    # RESTART PC
    # --------------------------------------------------------

    if any(
        phrase in message
        for phrase in [
            "restart my pc",
            "restart the computer",
            "reboot my pc",
        ]
    ):

        return system_actions.restart_pc()


    # --------------------------------------------------------
    # SCREENSHOT
    # --------------------------------------------------------

    if any(
        phrase in message
        for phrase in [
            "take a screenshot",
            "capture my screen",
            "screenshot this",
        ]
    ):

        return system_actions.take_screenshot()


    # --------------------------------------------------------
    # FLIP COIN
    # --------------------------------------------------------

    if any(
        phrase in message
        for phrase in [
            "flip a coin",
            "toss a coin",
            "heads or tails",
        ]
    ):

        return system_actions.flip_coin()


    # --------------------------------------------------------
    # ROLL DICE
    # --------------------------------------------------------

    if (
        "roll a dice" in message
        or "roll the dice" in message
    ):

        return system_actions.roll_dice()


    # --------------------------------------------------------
    # NO COMMAND FOUND
    # --------------------------------------------------------

    return None


# ============================================================
# MAIN RESPONSE FUNCTION
# ============================================================

def get_response(message):
    """
    Main entry point for SARATHI.

    First:
        Check deterministic PC commands.

    Then:
        Check time/date.

    Finally:
        Send the message to Ollama (Hinglish reply).
    """

    message = message.lower().strip()


    # --------------------------------------------------------
    # DIRECT COMPUTER COMMANDS
    # --------------------------------------------------------

    command_result = _handle_commands(
        message
    )

    if command_result is not None:

        return command_result


    # --------------------------------------------------------
    # CURRENT TIME
    # --------------------------------------------------------

    if "time" in message:

        current_time = datetime.now().strftime(
            "%I:%M %p"
        )

        return (
            f"The current time is {current_time}."
        )


    # --------------------------------------------------------
    # CURRENT DATE
    # --------------------------------------------------------

    if (
        "date" in message
        or "today" in message
    ):

        today = datetime.now().strftime(
            "%A, %d %B %Y"
        )

        return (
            f"Today is {today}."
        )


    # --------------------------------------------------------
    # SEND EVERYTHING ELSE TO OLLAMA
    # --------------------------------------------------------

    return _ask_ollama(
        message
    )