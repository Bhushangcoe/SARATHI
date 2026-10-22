import json
import re
from typing import Any

from groq import Groq


MODEL_NAME = "openai/gpt-oss-20b"


ALLOWED_ACTIONS = {
    "open_youtube",
    "youtube_search",
    "youtube_play_first",
    "youtube_pause",
    "youtube_resume",
    "youtube_next",
    "youtube_previous",
    "youtube_skip_forward",
    "youtube_skip_backward",
    "youtube_mute",
    "youtube_unmute",
    "youtube_volume_up",
    "youtube_volume_down",
    "youtube_fullscreen",
    "youtube_exit_fullscreen",
    "youtube_skip_ad",

    "open_instagram",
    "instagram_open_profile",
    "instagram_open_messages",
    "instagram_open_notifications",
    "instagram_search",
    "instagram_scroll_down",
    "instagram_scroll_up",
    "instagram_next_reel",
    "instagram_previous_reel",
    "instagram_pause_reel",
    "instagram_resume_reel",
    "instagram_open_reels",

    "instagram_like",
    "instagram_save",
    "instagram_follow",
    "instagram_unfollow",
    "instagram_send_message",

    "instagram_create_post",
    "instagram_create_story",
    "instagram_create_reel",

    "browser_open",
    "browser_search",

    "desktop_screenshot",

    "shutdown",
    "restart",
    "delete_file",
    "empty_recycle_bin",
}


PLANNER_PROMPT = """
You are the task planner for SARATHI, a desktop AI assistant.

Your job is to convert the user's natural-language request into a JSON task plan.

IMPORTANT:
You may ONLY use actions from the allowed action list.

Never invent an action.
Never generate Python.
Never generate shell commands.
Never generate arbitrary URLs except when using browser_open.
Never execute anything yourself.

Return ONLY valid JSON.

Format:

{
  "tasks": [
    {
      "action": "action_name",
      "args": {}
    }
  ]
}

Allowed actions:

open_youtube
youtube_search
youtube_play_first
youtube_pause
youtube_resume
youtube_next
youtube_previous
youtube_skip_forward
youtube_skip_backward
youtube_mute
youtube_unmute
youtube_volume_up
youtube_volume_down
youtube_fullscreen
youtube_exit_fullscreen
youtube_skip_ad

open_instagram
instagram_open_profile
instagram_open_messages
instagram_open_notifications
instagram_search
instagram_scroll_down
instagram_scroll_up
instagram_next_reel
instagram_previous_reel
instagram_pause_reel
instagram_resume_reel
instagram_open_reels
instagram_like
instagram_save
instagram_follow
instagram_unfollow
instagram_send_message
instagram_create_post
instagram_create_story
instagram_create_reel

browser_open
browser_search

desktop_screenshot

shutdown
restart
delete_file
empty_recycle_bin

Examples:

User:
"open youtube"

{
  "tasks": [
    {
      "action": "open_youtube",
      "args": {}
    }
  ]
}

User:
"search youtube for fast bowling drills and play the first video"

{
  "tasks": [
    {
      "action": "open_youtube",
      "args": {}
    },
    {
      "action": "youtube_search",
      "args": {
        "query": "fast bowling drills"
      }
    },
    {
      "action": "youtube_play_first",
      "args": {}
    }
  ]
}

User:
"pause the video"

{
  "tasks": [
    {
      "action": "youtube_pause",
      "args": {}
    }
  ]
}

User:
"search instagram for virat kohli"

{
  "tasks": [
    {
      "action": "open_instagram",
      "args": {}
    },
    {
      "action": "instagram_search",
      "args": {
        "query": "virat kohli"
      }
    }
  ]
}

User:
"send Rahul a message saying I will reach in 10 minutes"

{
  "tasks": [
    {
      "action": "open_instagram",
      "args": {}
    },
    {
      "action": "instagram_send_message",
      "args": {
        "username": "Rahul",
        "message": "I will reach in 10 minutes"
      }
    }
  ]
}
"""


def _extract_json(text: str) -> dict:
    text = text.strip()

    text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    text = text.replace("```", "").strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("No JSON object found.")

    return json.loads(text[start:end + 1])


def _clean_plan(plan: dict) -> dict:
    if not isinstance(plan, dict):
        return {"tasks": []}

    tasks = plan.get("tasks", [])

    if not isinstance(tasks, list):
        return {"tasks": []}

    clean_tasks = []

    for task in tasks:
        if not isinstance(task, dict):
            continue

        action = task.get("action")

        if action not in ALLOWED_ACTIONS:
            continue

        args = task.get("args", {})

        if not isinstance(args, dict):
            args = {}

        clean_tasks.append({
            "action": action,
            "args": args
        })

    return {
        "tasks": clean_tasks
    }


def plan_task(user_message: str) -> dict:
    client = Groq()

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": PLANNER_PROMPT
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        temperature=0,
        max_tokens=700,
    )

    content = response.choices[0].message.content or ""

    try:
        plan = _extract_json(content)
        return _clean_plan(plan)

    except Exception as exc:
        print(f"[SARATHI] Planner error: {exc}")
        return {"tasks": []}