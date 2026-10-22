
"""SARATHI core assistant: deterministic commands, task agent, and Groq chat."""

import subprocess
import webbrowser
from datetime import datetime

from core import system_actions
from core.brain import get_reply

# Keep the task agent optional so normal assistant features still work.
try:
    from core.task_planner import plan_task
    from core.task_engine import execute_plan
except Exception as agent_import_error:
    plan_task = None
    execute_plan = None
    print(f"[SARATHI] Task agent unavailable: {agent_import_error}")


def _should_use_task_agent(message: str) -> bool:
    """Identify clear browser automation and control requests."""
    text = message.lower().strip()

    phrases = (
        "open instagram",
        "open instagram messages",
        "open instagram notifications",
        "open instagram reels",
        "search instagram",
        "scroll instagram",
        "next reel",
        "previous reel",
        "pause reel",
        "resume reel",
        "like this post",
        "save this post",
        "follow this account",
        "unfollow this account",
        "send an instagram message",
        "send instagram message",
        "skip ad",
        "skip the ad",
        "pause the video",
        "resume the video",
        "next video",
        "previous video",
        "skip forward",
        "skip backward",
        "fast forward",
        "rewind the video",
        "mute the video",
        "unmute the video",
        "turn the volume up",
        "turn the volume down",
        "make the video fullscreen",
        "exit fullscreen",
        "play the first video",
        "play first video",
    )

    if any(phrase in text for phrase in phrases):
        return True

    has_platform = "youtube" in text or "instagram" in text
    has_sequence = any(
        phrase in text
        for phrase in (" and then ", " then ", " after that ", " and also ")
    )

    return has_platform and has_sequence


def run_agent_task(message, confirm_callback=None):
    """Plan and execute tasks using the project's task engine."""
    if plan_task is None or execute_plan is None:
        return (
            "The task agent is unavailable. "
            "Check its imports and dependencies."
        )

    try:
        print("[SARATHI] Planning task...")

        plan = plan_task(message)

        if (
            not isinstance(plan, dict)
            or not isinstance(plan.get("tasks"), list)
            or not plan["tasks"]
        ):
            return (
                "I couldn't create a valid task plan. "
                "Please try a simpler command."
            )

        print("[SARATHI] Planned tasks:", plan)

        success, result = execute_plan(
            plan,
            confirm_callback=confirm_callback,
        )

        return str(result)

    except Exception as error:
        print(f"[SARATHI] Task-agent error: {error}")
        return (
            "I couldn't complete that automated task. "
            "Please check the browser and task-agent setup."
        )


def _handle_commands(message):
    """Handle computer commands without calling the AI model."""

    # YouTube search
    if "search youtube for" in message or "youtube search for" in message:
        query = message.split("for", 1)[1].strip()
        return system_actions.search_youtube(query)

    if message.startswith("search youtube ") or message.startswith("youtube search "):
        query = message.split(" ", 2)[2].strip()
        return system_actions.search_youtube(query)

    # YouTube playback
    if message.startswith("play ") and "youtube" in message:
        query = (
            message.replace("play ", "", 1)
            .replace("on youtube", "")
            .replace("youtube", "")
            .strip()
        )
        return system_actions.play_youtube_video(query)

    if message.startswith("play "):
        query = message.replace("play ", "", 1).strip()
        return system_actions.play_youtube_video(query)

    # Google search
    if message.startswith("search for "):
        query = message.replace("search for ", "", 1).strip()
        return system_actions.search_google(query)

    if message.startswith("search "):
        query = message.replace("search ", "", 1).strip()
        return system_actions.search_google(query)

    # Open Google or YouTube
    if "google" in message and any(
        phrase in message for phrase in ("open", "go to")
    ):
        webbrowser.open("https://www.google.com")
        return "Opening Google for you."

    if (
        "youtube" in message
        and any(phrase in message for phrase in ("open", "go to"))
        and "search" not in message
    ):
        webbrowser.open("https://www.youtube.com")
        return "What would you like to watch?"

    # Open browser
    if any(
        phrase in message
        for phrase in ("open browser", "open my browser", "launch browser")
    ):
        return system_actions.open_browser()

    # Open common folders
    for folder_name in (
        "documents",
        "downloads",
        "desktop",
        "pictures",
        "music",
        "videos",
    ):
        if f"open {folder_name}" in message:
            return system_actions.open_folder(folder_name)

    if any(
        phrase in message
        for phrase in (
            "open this pc",
            "open my computer",
            "open file explorer",
            "open explorer",
        )
    ):
        return system_actions.open_folder("this pc")

    # Notes
    if message.startswith(("write a note", "take a note", "make a note")):
        for splitter in ("that", "saying", ":"):
            if splitter in message:
                note_text = message.split(splitter, 1)[1].strip()
                return system_actions.write_note(note_text)

        return "What would you like me to write down?"

    # Internet and system checks
    if any(
        phrase in message
        for phrase in (
            "check my internet",
            "is my internet working",
            "check internet connection",
        )
    ):
        return system_actions.check_internet()

    if any(
        phrase in message
        for phrase in (
            "check disk space",
            "how much space do i have",
            "check storage",
        )
    ):
        return system_actions.check_disk_space()

    if any(
        phrase in message
        for phrase in ("flush dns", "fix my dns", "reset dns")
    ):
        return system_actions.flush_dns()

    if any(
        phrase in message
        for phrase in (
            "clear temp files",
            "clean temp files",
            "clear temporary files",
        )
    ):
        return system_actions.clear_temp_files()

    if any(
        phrase in message
        for phrase in (
            "empty recycle bin",
            "empty the recycle bin",
            "empty trash",
        )
    ):
        return system_actions.empty_recycle_bin()

    if any(
        phrase in message
        for phrase in (
            "ongoing conflicts",
            "current conflicts",
            "world conflicts",
            "wars going on",
            "current wars",
            "what wars are happening",
        )
    ):
        return system_actions.search_google(
            "current ongoing conflicts in the world"
        )

    if any(
        phrase in message
        for phrase in (
            "check my pc",
            "find problems",
            "run a checkup",
            "fix my computer",
            "check my computer",
        )
    ):
        return system_actions.run_quick_checkup()

    # Close applications
    if message.startswith(("close ", "quit ", "exit ")):
        app_name = message

        for prefix in ("close ", "quit ", "exit "):
            if app_name.startswith(prefix):
                app_name = app_name.replace(prefix, "", 1)
                break

        app_name = (
            app_name.replace("the ", "")
            .replace("my ", "")
            .strip()
        )

        return system_actions.close_app(app_name)

    # Common Windows applications
    if any(
        phrase in message
        for phrase in ("open notepad", "launch notepad", "start notepad")
    ):
        subprocess.Popen(["notepad.exe"])
        return "Opening Notepad for you."

    if any(
        phrase in message
        for phrase in ("open calculator", "launch calculator", "open calc")
    ):
        subprocess.Popen(["calc.exe"])
        return "Opening Calculator for you."

    if any(
        phrase in message
        for phrase in ("open gmail", "open email", "check my email")
    ):
        webbrowser.open("https://mail.google.com")
        return "Opening Gmail for you."

    for app_name in (
        "word",
        "excel",
        "powerpoint",
        "paint",
        "task manager",
        "control panel",
        "settings",
        "command prompt",
        "snipping tool",
    ):
        if f"open {app_name}" in message:
            return system_actions.open_app(app_name)

    # Power commands
    if any(
        phrase in message
        for phrase in (
            "lock my pc",
            "lock the pc",
            "lock my computer",
            "lock computer",
        )
    ):
        return system_actions.lock_pc()

    if "cancel shutdown" in message:
        return system_actions.cancel_shutdown()

    if any(
        phrase in message
        for phrase in (
            "shut down my pc",
            "shutdown my pc",
            "shut down the computer",
            "turn off my pc",
        )
    ):
        return system_actions.shutdown_pc()

    if any(
        phrase in message
        for phrase in (
            "restart my pc",
            "restart the computer",
            "reboot my pc",
        )
    ):
        return system_actions.restart_pc()

    # Screenshot, coin, and dice
    if any(
        phrase in message
        for phrase in (
            "take a screenshot",
            "capture my screen",
            "screenshot this",
        )
    ):
        return system_actions.take_screenshot()

    if any(
        phrase in message
        for phrase in ("flip a coin", "toss a coin", "heads or tails")
    ):
        return system_actions.flip_coin()

    if "roll a dice" in message or "roll the dice" in message:
        return system_actions.roll_dice()

    return None


def get_response(message, confirm_callback=None):
    """Main response entry point used by the UI."""
    original_message = str(message or "").strip()

    if not original_message:
        return "I didn't hear anything."

    normalized_message = original_message.lower().strip()

    # Browser automation before generic website handlers
    if _should_use_task_agent(normalized_message):
        return run_agent_task(
            original_message,
            confirm_callback=confirm_callback,
        )

    # Existing deterministic commands
    command_result = _handle_commands(normalized_message)

    if command_result is not None:
        return command_result

    # Time
    if (
        normalized_message == "time"
        or "what time is it" in normalized_message
        or "current time" in normalized_message
    ):
        current_time = datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}."

    # Date
    if (
        normalized_message == "date"
        or "what is today's date" in normalized_message
        or "what is the date today" in normalized_message
        or "today's date" in normalized_message
    ):
        today = datetime.now().strftime("%A, %d %B %Y")
        return f"Today is {today}."

    # General conversation through Groq
    return get_reply(original_message)
