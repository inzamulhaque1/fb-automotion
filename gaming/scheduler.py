"""
Gaming Scheduler - Schedule video uploads throughout the day
=============================================================
"""

import os
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

from config.schedule import GAMING_SCHEDULE
from gaming.uploader import get_pending_videos, upload_video

logger = logging.getLogger("GamingScheduler")


class GamingScheduler:
    """Manages scheduled video uploads for INZ-Gaming page."""

    def __init__(self):
        self.timezone = pytz.timezone(GAMING_SCHEDULE["timezone"])
        self.scheduler = BackgroundScheduler(timezone=self.timezone)
        self.upload_queue = []
        self.today_uploads = 0

    def load_queue(self):
        """Load pending videos into upload queue."""
        self.upload_queue = get_pending_videos()
        logger.info(f"[*] Queue loaded: {len(self.upload_queue)} videos")

    def schedule_today(self):
        """Schedule uploads for today's time slots."""
        self.load_queue()

        now = datetime.now(self.timezone)
        time_slots = GAMING_SCHEDULE["time_slots"]

        for i, time_str in enumerate(time_slots):
            hour, minute = map(int, time_str.split(":"))
            scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # Skip past time slots
            if scheduled_time <= now:
                continue

            # Skip if no more videos in queue
            if i >= len(self.upload_queue):
                break

            video_path = self.upload_queue[i]
            self.scheduler.add_job(
                self._upload_job,
                "date",
                run_date=scheduled_time,
                args=[video_path],
                id=f"gaming_upload_{i}",
                replace_existing=True,
            )
            logger.info(f"[+] Scheduled: {os.path.basename(video_path)} at {time_str}")

        self.today_uploads = 0

    def _upload_job(self, video_path):
        """Execute a scheduled upload."""
        if not os.path.exists(video_path):
            logger.warning(f"[!] Video not found: {video_path}")
            return

        logger.info(f"[*] Scheduled upload starting: {os.path.basename(video_path)}")
        result = upload_video(video_path)
        self.today_uploads += 1
        logger.info(f"[+] Upload {self.today_uploads}/{GAMING_SCHEDULE['posts_per_day']} done")

    def start(self):
        """Start the scheduler."""
        self.schedule_today()

        # Re-schedule every day at midnight
        self.scheduler.add_job(
            self.schedule_today,
            "cron",
            hour=0,
            minute=5,
            id="gaming_daily_reschedule",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info("[*] Gaming scheduler started")

    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown(wait=False)
        logger.info("[*] Gaming scheduler stopped")

    def get_status(self):
        """Get scheduler status."""
        jobs = self.scheduler.get_jobs()
        return {
            "running": self.scheduler.running,
            "pending_jobs": len(jobs),
            "today_uploads": self.today_uploads,
            "queue_size": len(self.upload_queue),
            "jobs": [
                {
                    "id": job.id,
                    "next_run": str(job.next_run_time),
                }
                for job in jobs
            ],
        }
