"""
Video Effects - Zoom, color grading, transitions
=================================================
Lightweight effects that work well on mid-spec PC.
"""

import os
import logging
import random
from moviepy import VideoFileClip, CompositeVideoClip, concatenate_videoclips

logger = logging.getLogger("Effects")


def add_zoom_effect(input_path, output_path=None, zoom_points=3):
    """
    Add random zoom-in effects at key moments.
    Lightweight: just crops and resizes at specific timestamps.
    """
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_fx{ext}"

    video = VideoFileClip(input_path)
    w, h = video.size
    duration = video.duration

    # Create zoom segments
    segments = []
    segment_length = duration / (zoom_points * 2 + 1)

    for i in range(zoom_points * 2 + 1):
        start = i * segment_length
        end = min((i + 1) * segment_length, duration)

        if end - start < 0.5:
            continue

        segment = video.subclipped(start, end)

        # Every other segment gets a zoom
        if i % 2 == 1:
            zoom_factor = random.uniform(1.1, 1.3)
            new_w = int(w / zoom_factor)
            new_h = int(h / zoom_factor)
            x_offset = (w - new_w) // 2
            y_offset = (h - new_h) // 2

            segment = segment.cropped(
                x1=x_offset, y1=y_offset,
                x2=x_offset + new_w, y2=y_offset + new_h
            )
            segment = segment.resized((w, h))

        segments.append(segment)

    if segments:
        final = concatenate_videoclips(segments)
        final.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            logger=None,
            threads=2,
        )
        final.close()
    else:
        import shutil
        shutil.copy2(input_path, output_path)

    video.close()
    logger.info(f"[+] Zoom effects added -> {output_path}")
    return output_path


def apply_color_grade(input_path, output_path=None, style="gaming"):
    """
    Apply simple color grading for gaming vibe.
    Increases contrast and saturation slightly.
    """
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_graded{ext}"

    video = VideoFileClip(input_path)

    if style == "gaming":
        # Slightly boost contrast
        def adjust_frame(frame):
            import numpy as np
            adjusted = frame.astype(float)
            adjusted = ((adjusted - 128) * 1.15) + 128  # Contrast boost
            adjusted = np.clip(adjusted, 0, 255).astype("uint8")
            return adjusted

        graded = video.image_transform(adjust_frame)
    else:
        graded = video

    graded.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        logger=None,
        threads=2,
    )

    graded.close()
    video.close()

    logger.info(f"[+] Color grading applied -> {output_path}")
    return output_path
