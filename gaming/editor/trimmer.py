"""
Video Trimmer - Auto trim long videos into clips
=================================================
Splits long gameplay recordings into 3/5/8 minute clips.
"""

import os
import random
import logging
from moviepy import VideoFileClip

from config.settings import GAMING

logger = logging.getLogger("Trimmer")


def get_trim_duration():
    """Get a random duration from configured lengths."""
    minutes = random.choice(GAMING["video_lengths"])
    return minutes * 60


def trim_video(input_path, output_dir, num_clips=None):
    """
    Trim a long video into multiple clips.

    Args:
        input_path: Path to the raw video
        output_dir: Directory to save trimmed clips
        num_clips: Number of clips to extract (auto-calculated if None)

    Returns:
        List of trimmed clip paths
    """
    os.makedirs(output_dir, exist_ok=True)
    clip = VideoFileClip(input_path)
    total_duration = clip.duration

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    trimmed_clips = []
    current_time = 0
    clip_index = 1

    if num_clips is None:
        avg_clip_len = sum(GAMING["video_lengths"]) / len(GAMING["video_lengths"]) * 60
        num_clips = max(1, int(total_duration / avg_clip_len))

    while current_time < total_duration and clip_index <= num_clips:
        clip_duration = get_trim_duration()
        end_time = min(current_time + clip_duration, total_duration)

        # Skip if remaining is too short (less than 60 seconds)
        if end_time - current_time < 60:
            break

        output_path = os.path.join(
            output_dir, f"{base_name}_clip{clip_index:02d}.mp4"
        )

        sub_clip = clip.subclipped(current_time, end_time)
        sub_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            logger=None,
            threads=2,
        )
        sub_clip.close()

        trimmed_clips.append(output_path)
        logger.info(f"[+] Clip {clip_index}: {current_time:.0f}s - {end_time:.0f}s -> {output_path}")

        current_time = end_time
        clip_index += 1

    clip.close()
    return trimmed_clips


def smart_trim(input_path, output_dir, target_duration=None):
    """
    Trim a single clip to target duration from the best part.
    If video is shorter than target, returns as-is.
    """
    os.makedirs(output_dir, exist_ok=True)
    clip = VideoFileClip(input_path)

    if target_duration is None:
        target_duration = get_trim_duration()

    if clip.duration <= target_duration:
        output_path = os.path.join(output_dir, os.path.basename(input_path))
        clip.write_videofile(output_path, codec="libx264", audio_codec="aac", logger=None, threads=2)
        clip.close()
        return output_path

    # Start from a random point (avoiding first/last 10 seconds)
    margin = min(10, clip.duration * 0.05)
    max_start = clip.duration - target_duration - margin
    start = random.uniform(margin, max(margin, max_start))
    end = start + target_duration

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}_trimmed.mp4")

    sub_clip = clip.subclipped(start, end)
    sub_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", logger=None, threads=2)
    sub_clip.close()
    clip.close()

    return output_path
