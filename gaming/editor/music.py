"""
Background Music - Auto add music to gaming videos
===================================================
Adds background music from assets/music/ folder.
"""

import os
import random
import logging
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip

from config.settings import MUSIC_DIR, GAMING

logger = logging.getLogger("Music")

SUPPORTED_AUDIO = {".mp3", ".wav", ".ogg", ".m4a", ".aac"}


def get_random_music():
    """Pick a random music file from assets/music/."""
    if not os.path.exists(MUSIC_DIR):
        return None

    music_files = [
        os.path.join(MUSIC_DIR, f)
        for f in os.listdir(MUSIC_DIR)
        if os.path.splitext(f)[1].lower() in SUPPORTED_AUDIO
    ]

    if not music_files:
        return None

    return random.choice(music_files)


def add_background_music(input_path, output_path=None, music_path=None, volume=None):
    """
    Add background music to a video.

    Args:
        input_path: Path to input video
        output_path: Output path (auto if None)
        music_path: Music file path (random if None)
        volume: Music volume 0.0-1.0 (from config if None)

    Returns:
        Path to output video
    """
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_music{ext}"

    if music_path is None:
        music_path = get_random_music()

    if music_path is None:
        logger.warning("[!] No music files found in assets/music/. Skipping.")
        # Copy video as-is
        import shutil
        shutil.copy2(input_path, output_path)
        return output_path

    if volume is None:
        volume = GAMING["music_volume"]

    video = VideoFileClip(input_path)
    music = AudioFileClip(music_path)

    # Loop music if shorter than video
    if music.duration < video.duration:
        loops_needed = int(video.duration / music.duration) + 1
        from moviepy import concatenate_audioclips
        music = concatenate_audioclips([music] * loops_needed)

    # Trim music to video length
    music = music.subclipped(0, video.duration)

    # Set music volume
    music = music.with_volume_scaled(volume)

    # Mix original audio with music
    if video.audio is not None:
        final_audio = CompositeAudioClip([video.audio, music])
    else:
        final_audio = music

    final_video = video.with_audio(final_audio)
    final_video.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        logger=None,
        threads=2,
    )

    final_video.close()
    video.close()
    music.close()

    logger.info(f"[+] Music added: {os.path.basename(music_path)} -> {output_path}")
    return output_path
