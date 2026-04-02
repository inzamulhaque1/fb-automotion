"""
Gaming Editor Pipeline - Full auto edit workflow
=================================================
Connects: Trim → Effects → Text → Music → Watermark
"""

import os
import shutil
import logging
import tempfile

from config.settings import OUTPUT_GAMING_DIR
from gaming.editor.trimmer import trim_video, smart_trim
from gaming.editor.text_overlay import add_text_overlay, add_intro_text
from gaming.editor.music import add_background_music
from gaming.editor.effects import add_zoom_effect, apply_color_grade
from gaming.editor.watermark import add_watermark

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GamingPipeline")


def process_video(input_path, add_intro=True, add_music=True,
                  add_effects=True, add_wm=True):
    """
    Full gaming video processing pipeline.

    Steps:
    1. Trim video into clips
    2. For each clip:
       a. Add intro/outro text
       b. Apply color grading
       c. Add zoom effects
       d. Add text overlay (INZ-Gaming)
       e. Add background music
       f. Add watermark
    3. Save to output/gaming/

    Returns:
        List of processed video paths
    """
    logger.info(f"[*] Processing: {os.path.basename(input_path)}")

    # Create temp directory for intermediate files
    temp_dir = tempfile.mkdtemp(prefix="inz_gaming_")
    processed_videos = []

    try:
        # Step 1: Trim into clips
        logger.info("[1/6] Trimming video into clips...")
        trim_dir = os.path.join(temp_dir, "trimmed")
        clips = trim_video(input_path, trim_dir)

        if not clips:
            # If video is short, use as single clip
            clips = [input_path]

        for i, clip_path in enumerate(clips):
            logger.info(f"\n[*] Processing clip {i+1}/{len(clips)}")
            current = clip_path

            # Step 2: Add intro/outro
            if add_intro:
                logger.info("[2/6] Adding intro/outro...")
                intro_path = os.path.join(temp_dir, f"intro_{i}.mp4")
                current = add_intro_text(current, intro_path)

            # Step 3: Color grading
            if add_effects:
                logger.info("[3/6] Applying color grading...")
                graded_path = os.path.join(temp_dir, f"graded_{i}.mp4")
                current = apply_color_grade(current, graded_path)

            # Step 4: Zoom effects
            if add_effects:
                logger.info("[4/6] Adding zoom effects...")
                zoom_path = os.path.join(temp_dir, f"zoom_{i}.mp4")
                current = add_zoom_effect(current, zoom_path, zoom_points=2)

            # Step 5: Text overlay
            logger.info("[5/6] Adding text overlay...")
            text_path = os.path.join(temp_dir, f"text_{i}.mp4")
            current = add_text_overlay(current, text_path)

            # Step 6: Background music
            if add_music:
                logger.info("[6/6] Adding background music...")
                music_path = os.path.join(temp_dir, f"music_{i}.mp4")
                current = add_background_music(current, music_path)

            # Step 7: Watermark
            if add_wm:
                logger.info("[+] Adding watermark...")
                wm_path = os.path.join(temp_dir, f"wm_{i}.mp4")
                current = add_watermark(current, wm_path)

            # Move final to output
            os.makedirs(OUTPUT_GAMING_DIR, exist_ok=True)
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            final_name = f"{base_name}_final_{i+1:02d}.mp4"
            final_path = os.path.join(OUTPUT_GAMING_DIR, final_name)
            shutil.move(current, final_path)

            processed_videos.append(final_path)
            logger.info(f"[✓] Saved: {final_path}")

    finally:
        # Cleanup temp files
        shutil.rmtree(temp_dir, ignore_errors=True)

    logger.info(f"\n[✓] Done! {len(processed_videos)} videos processed.")
    return processed_videos


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        results = process_video(sys.argv[1])
        print(f"\nProcessed {len(results)} videos:")
        for v in results:
            print(f"  {v}")
    else:
        print("Usage: python -m gaming.editor.pipeline <video_path>")
