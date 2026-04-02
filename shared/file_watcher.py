"""
File Watcher - Auto-detect new videos in input folder
======================================================
Watches input/raw_videos/ for new files and triggers processing.
"""

import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from config.settings import INPUT_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FileWatcher")

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".m4v", ".webm"}


class VideoHandler(FileSystemEventHandler):
    """Handles new video file events."""

    def __init__(self, callback=None):
        self.callback = callback
        self._processing = set()

    def on_created(self, event):
        if event.is_directory:
            return

        ext = os.path.splitext(event.src_path)[1].lower()
        if ext not in VIDEO_EXTENSIONS:
            return

        filepath = event.src_path
        if filepath in self._processing:
            return

        self._processing.add(filepath)
        logger.info(f"[+] New video detected: {os.path.basename(filepath)}")

        # Wait for file to finish writing
        self._wait_for_complete(filepath)

        if self.callback:
            self.callback(filepath)

        self._processing.discard(filepath)

    def _wait_for_complete(self, filepath, timeout=300):
        """Wait until file size stops changing (upload complete)."""
        last_size = -1
        stable_count = 0

        while stable_count < 3 and timeout > 0:
            try:
                current_size = os.path.getsize(filepath)
                if current_size == last_size:
                    stable_count += 1
                else:
                    stable_count = 0
                last_size = current_size
            except OSError:
                pass
            time.sleep(2)
            timeout -= 2

        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        logger.info(f"    Upload complete: {size_mb:.1f} MB")


def start_watcher(callback=None):
    """Start watching the input directory for new videos."""
    os.makedirs(INPUT_DIR, exist_ok=True)

    handler = VideoHandler(callback=callback)
    observer = Observer()
    observer.schedule(handler, INPUT_DIR, recursive=False)
    observer.start()

    logger.info(f"[*] Watching folder: {INPUT_DIR}")
    logger.info("[*] Waiting for new videos...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    def on_video(path):
        print(f"Ready to process: {path}")

    start_watcher(callback=on_video)
