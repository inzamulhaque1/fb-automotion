"""
Watermark - Add subtle watermark to prevent content theft
=========================================================
Adds a semi-transparent text watermark.
"""

import os
import logging
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

from config.settings import GAMING

logger = logging.getLogger("Watermark")


def add_watermark(input_path, output_path=None, text=None, opacity=0.4):
    """
    Add a subtle watermark to the video.

    Args:
        input_path: Input video path
        output_path: Output path
        text: Watermark text (defaults to page name)
        opacity: Watermark opacity (0.0 - 1.0)

    Returns:
        Output video path
    """
    if text is None:
        text = GAMING["watermark_text"]

    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_wm{ext}"

    video = VideoFileClip(input_path)

    # Small watermark in bottom-right
    wm_clip = TextClip(
        text=text,
        font_size=24,
        color="white",
        font="Arial",
        stroke_color="black",
        stroke_width=1,
    )
    wm_clip = wm_clip.with_duration(video.duration)
    wm_clip = wm_clip.with_position(("right", "bottom"), relative=True)
    wm_clip = wm_clip.with_opacity(opacity)

    final = CompositeVideoClip([video, wm_clip])
    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        logger=None,
        threads=2,
    )

    final.close()
    video.close()
    wm_clip.close()

    logger.info(f"[+] Watermark added -> {output_path}")
    return output_path
