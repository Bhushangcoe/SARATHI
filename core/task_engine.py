from core.permissions import (
    confirmation_message,
    needs_confirmation,
)

from skills import youtube
from skills import instagram
from skills import browser
from skills import desktop


ACTION_MAP = {

    # YouTube
    "open_youtube": youtube.open_youtube,
    "youtube_search": youtube.search_youtube,
    "youtube_play_first": youtube.play_first_video,
    "youtube_pause": youtube.pause,
    "youtube_resume": youtube.resume,
    "youtube_next": youtube.next_video,
    "youtube_previous": youtube.previous_video,
    "youtube_skip_forward": youtube.skip_forward,
    "youtube_skip_backward": youtube.skip_backward,
    "youtube_mute": youtube.mute,
    "youtube_unmute": youtube.unmute,
    "youtube_volume_up": youtube.volume_up,
    "youtube_volume_down": youtube.volume_down,
    "youtube_fullscreen": youtube.fullscreen,
    "youtube_exit_fullscreen": youtube.exit_fullscreen,
    "youtube_skip_ad": youtube.skip_ad,

    # Instagram
    "open_instagram": instagram.open_instagram,
    "instagram_open_profile": instagram.open_profile,
    "instagram_open_messages": instagram.open_messages,
    "instagram_open_notifications": instagram.open_notifications,
    "instagram_search": instagram.search,
    "instagram_scroll_down": instagram.scroll_down,
    "instagram_scroll_up": instagram.scroll_up,
    "instagram_next_reel": instagram.next_reel,
    "instagram_previous_reel": instagram.previous_reel,
    "instagram_pause_reel": instagram.pause_reel,
    "instagram_resume_reel": instagram.resume_reel,
    "instagram_open_reels": instagram.open_reels,

    "instagram_like": instagram.like,
    "instagram_save": instagram.save,
    "instagram_follow": instagram.follow,
    "instagram_unfollow": instagram.unfollow,
    "instagram_send_message": instagram.send_message,

    "instagram_create_post": instagram.create_post,
    "instagram_create_story": instagram.create_story,
    "instagram_create_reel": instagram.create_reel,

    # Browser
    "browser_open": browser.open_url,
    "browser_search": browser.search_web,

    # Desktop
    "desktop_screenshot": desktop.screenshot,
}


def execute_task(task: dict, confirm_callback=None):
    action = task.get("action")
    args = task.get("args", {})

    if action not in ACTION_MAP:
        return False, f"I don't have an action called {action}."

    if needs_confirmation(action):

        if confirm_callback is None:
            return False, "This action requires confirmation."

        message = confirmation_message(
            action,
            args
        )

        approved = confirm_callback(message)

        if not approved:
            return False, "Action cancelled."

    function = ACTION_MAP[action]

    try:
        result = function(**args)

        if isinstance(result, tuple):
            return result

        return True, str(result)

    except TypeError as exc:
        return False, f"Invalid arguments for {action}: {exc}"

    except Exception as exc:
        print(f"[SARATHI] Task error: {exc}")

        return False, f"I couldn't complete {action}."


def execute_plan(plan: dict, confirm_callback=None):
    tasks = plan.get("tasks", [])

    if not tasks:
        return False, "I couldn't turn that request into a supported task."

    results = []

    for index, task in enumerate(tasks, start=1):

        print(
            f"[SARATHI] Task {index}/{len(tasks)}: "
            f"{task.get('action')}"
        )

        success, message = execute_task(
            task,
            confirm_callback=confirm_callback
        )

        results.append(message)

        if not success:
            return False, message

    return True, " ".join(results)