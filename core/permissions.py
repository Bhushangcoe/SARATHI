from typing import Optional


SAFE_ACTIONS = {
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
    "browser_open",
    "browser_search",
    "desktop_screenshot",
}


CONFIRM_ACTIONS = {
    "instagram_like",
    "instagram_save",
    "instagram_follow",
    "instagram_unfollow",
    "instagram_send_message",
    "instagram_create_post",
    "instagram_create_story",
    "instagram_create_reel",
    "send_email",
}


DANGEROUS_ACTIONS = {
    "shutdown",
    "restart",
    "delete_file",
    "empty_recycle_bin",
    "publish_social_post",
}


def permission_for(action: str) -> str:
    if action in DANGEROUS_ACTIONS:
        return "dangerous"

    if action in CONFIRM_ACTIONS:
        return "confirm"

    return "safe"


def needs_confirmation(action: str) -> bool:
    return permission_for(action) in {"confirm", "dangerous"}


def confirmation_message(action: str, args: dict) -> str:
    if action == "instagram_send_message":
        return f"You're about to send a message to {args.get('username', 'the selected user')}. Send it?"

    if action in {
        "instagram_create_post",
        "instagram_create_story",
        "instagram_create_reel",
        "publish_social_post",
    }:
        return "The social-media content is ready. Do you want me to publish it?"

    if action == "instagram_follow":
        return "Do you want me to follow this account?"

    if action == "instagram_unfollow":
        return "Do you want me to unfollow this account?"

    if action == "instagram_like":
        return "Do you want me to like this post?"

    if action == "instagram_save":
        return "Do you want me to save this post?"

    if action == "shutdown":
        return "You're about to shut down the computer. Should I continue?"

    if action == "restart":
        return "You're about to restart the computer. Should I continue?"

    if action == "delete_file":
        return f"You're about to delete {args.get('path', 'this file')}. Should I continue?"

    if action == "empty_recycle_bin":
        return "This will permanently remove items from the Recycle Bin. Should I continue?"

    return "This action requires confirmation. Should I continue?"