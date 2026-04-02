"""
Text Overlay - Add INZ-Gaming text branding to videos
=====================================================
Adds page name text overlay with gaming style.
"""

import os
import logging
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

from config.settings import GAMING

logger = logging.getLogger("TextOverlay")


def add_text_overlay(input_path, output_path=None, text=None, position="top-right"):
    """
    Add text overlay to video.

    Args:
        input_path: Path to input video
        output_path: Path to save (auto-generated if None)
        text: Text to overlay (defaults to page name)
        position: Where to place text

    Returns:
        Path to output video
    """
    if text is None:
        text = GAMING["watermark_text"]

    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_text{ext}"

    theme = GAMING["theme"]
    video = VideoFileClip(input_path)

    # Create text clip with gaming style
    txt_clip = TextClip(
        text=text,
        font_size=theme["font_size"],
        color=theme["text_color"],
        font="Arial-Bold",
        stroke_color=theme["primary"],  # Red stroke
        stroke_width=2,
    )
    txt_clip = txt_clip.with_duration(video.duration)

    # Position mapping
    positions = {
        "top-right": ("right", "top"),
        "top-left": ("left", "top"),
        "bottom-right": ("right", "bottom"),
        "bottom-left": ("left", "bottom"),
        "center": ("center", "center"),
    }
    pos = positions.get(position, ("right", "top"))
    txt_clip = txt_clip.with_position(pos, relative=True)
    txt_clip = txt_clip.with_opacity(0.8)

    # Composite video with text
    final = CompositeVideoClip([video, txt_clip])
    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        logger=None,
        threads=2,
    )

    final.close()
    video.close()
    txt_clip.close()

    logger.info(f"[+] Text overlay added: {text} -> {output_path}")
    return output_path


def add_intro_text(input_path, output_path=None, duration=3):
    """
    Add a text-based intro (INZ-Gaming name appears for 3 seconds).
    Red + Black theme, centered.
    """
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_intro{ext}"

    theme = GAMING["theme"]
    video = VideoFileClip(input_path)

    # Create intro text clip
    intro_txt = TextClip(
        text=GAMING["watermark_text"],
        font_size=72,
        color=theme["primary"],  # Red text
        font="Arial-Bold",
        stroke_color=theme["text_color"],  # White stroke
        stroke_width=3,
        bg_color=theme["secondary"],  # Black background
        size=video.size,
        text_align="center",
        method="caption",
    )
    intro_txt = intro_txt.with_duration(duration)

    # Add fade in/out
    intro_txt = intro_txt.with_effects([
        lambda clip: clip.crossfadein(0.5),
        lambda clip: clip.crossfadeout(0.5),
    ]) if hasattr(intro_txt, 'crossfadein') else intro_txt

    # Outro text
    outro_txt = TextClip(
        text=f"Follow {GAMING['watermark_text']}",
        font_size=56,
        color=theme["primary"],
        font="Arial-Bold",
        stroke_color=theme["text_color"],
        stroke_width=2,
        bg_color=theme["secondary"],
        size=video.size,
        text_align="center",
        method="caption",
    )
    outro_txt = outro_txt.with_duration(duration)

    from moviepy import concatenate_videoclips
    final = concatenate_videoclips([intro_txt, video, outro_txt])
    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        logger=None,
        threads=2,
    )

    final.close()
    video.close()

    logger.info(f"[+] Intro/Outro added -> {output_path}")
    return output_path
