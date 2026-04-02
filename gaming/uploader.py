"""
Gaming Video Uploader - Upload processed videos to FB
======================================================
"""

import os
import logging

from shared.fb_api import get_gaming_api
from config.settings import OUTPUT_GAMING_DIR, GAMING

logger = logging.getLogger("GamingUploader")

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".m4v", ".webm"}

# Gaming hashtags for reach
GAMING_HASHTAGS = [
    "#gaming", "#gamer", "#gameplay", "#gamingcommunity",
    "#freefire", "#efootball", "#minecraft",
    "#mobilegaming", "#gamingvideos", "#gaminglife",
    "#INZGaming", "#epicmoments", "#gamingclips",
]


def generate_caption(video_name):
    """Generate a caption for the gaming video."""
    # Extract game name from filename if possible
    name_lower = video_name.lower()

    if "freefire" in name_lower or "ff" in name_lower:
        game = "Free Fire"
        emoji = "🔥"
    elif "efootball" in name_lower or "pes" in name_lower or "football" in name_lower:
        game = "eFootball"
        emoji = "⚽"
    elif "minecraft" in name_lower or "mc" in name_lower:
        game = "Minecraft"
        emoji = "⛏️"
    else:
        game = "Gaming"
        emoji = "🎮"

    hashtags = " ".join(GAMING_HASHTAGS[:8])

    caption = (
        f"{emoji} {game} Gameplay | {GAMING['watermark_text']}\n\n"
        f"Watch till the end! 🔥\n"
        f"Follow {GAMING['watermark_text']} for daily gaming content!\n\n"
        f"{hashtags}"
    )
    return caption


def get_pending_videos():
    """Get list of videos ready to upload."""
    if not os.path.exists(OUTPUT_GAMING_DIR):
        return []

    videos = [
        os.path.join(OUTPUT_GAMING_DIR, f)
        for f in sorted(os.listdir(OUTPUT_GAMING_DIR))
        if os.path.splitext(f)[1].lower() in VIDEO_EXTENSIONS
    ]
    return videos


def upload_video(video_path, move_after=True):
    """
    Upload a single video to gaming page.

    Args:
        video_path: Path to the video
        move_after: Move to uploaded folder after success

    Returns:
        Upload result dict
    """
    api = get_gaming_api()
    video_name = os.path.basename(video_path)
    caption = generate_caption(video_name)

    logger.info(f"[*] Uploading: {video_name}")
    result = api.upload_video(video_path, title=video_name, description=caption)

    if "id" in result and move_after:
        # Move to uploaded subfolder
        uploaded_dir = os.path.join(OUTPUT_GAMING_DIR, "uploaded")
        os.makedirs(uploaded_dir, exist_ok=True)
        dest = os.path.join(uploaded_dir, video_name)
        os.rename(video_path, dest)
        logger.info(f"[+] Moved to uploaded/")

    return result


def upload_all_pending():
    """Upload all pending videos."""
    videos = get_pending_videos()
    if not videos:
        logger.info("[*] No pending videos to upload.")
        return []

    results = []
    for video in videos:
        result = upload_video(video)
        results.append(result)

    logger.info(f"[+] Uploaded {len(results)} videos.")
    return results
