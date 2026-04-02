"""
Personal Brand Scheduler - Text-first posting strategy
=========================================================
Focuses on text posts (like top influencers).
Image cards removed - text posts get better engagement.
"""

import os
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

from config.schedule import PERSONAL_SCHEDULE
from personal.content.post_writer import get_all_personal_content
from personal.uploader import upload_content

logger = logging.getLogger("PersonalScheduler")


class PersonalScheduler:
    """Manages scheduled content posting for personal brand page."""

    def __init__(self):
        self.timezone = pytz.timezone(PERSONAL_SCHEDULE["timezone"])
        self.scheduler = BackgroundScheduler(timezone=self.timezone)
        self.post_queue = []
        self.today_posts = 0

    def generate_daily_content(self):
        """Generate text-only content for today (influencer style)."""
        logger.info("[*] Generating daily content...")

        dist = PERSONAL_SCHEDULE["content_distribution"]

        # All text-based posts - no image cards
        all_posts = get_all_personal_content(
            ai_news_count=dist.get("ai_news", 3),
            tips_count=dist.get("web_dev_tips", 3),
            thread_count=dist.get("thread", 2),
        )

        self.post_queue = all_posts
        logger.info(f"[+] Generated {len(all_posts)} text posts for today")

    def schedule_today(self):
        """Schedule content for today's time slots."""
        self.generate_daily_content()

        now = datetime.now(self.timezone)
        time_slots = PERSONAL_SCHEDULE["time_slots"]

        for i, time_str in enumerate(time_slots):
            hour, minute = map(int, time_str.split(":"))
            scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            if scheduled_time <= now:
                continue

            if i >= len(self.post_queue):
                break

            post_data = self.post_queue[i]
            self.scheduler.add_job(
                self._post_job,
                "date",
                run_date=scheduled_time,
                args=[post_data],
                id=f"personal_post_{i}",
                replace_existing=True,
            )
            logger.info(f"[+] Scheduled: {post_data.get('title', 'post')[:40]} at {time_str}")

        self.today_posts = 0

    def _post_job(self, post_data):
        """Execute a scheduled post."""
        logger.info(f"[*] Posting: {post_data.get('title', 'post')[:40]}...")
        result = upload_content(post_data)
        self.today_posts += 1
        logger.info(f"[+] Post {self.today_posts}/{PERSONAL_SCHEDULE['posts_per_day']} done")

    def start(self):
        """Start the scheduler."""
        self.schedule_today()

        self.scheduler.add_job(
            self.schedule_today,
            "cron",
            hour=0,
            minute=10,
            id="personal_daily_reschedule",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info("[*] Personal scheduler started")

    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown(wait=False)
        logger.info("[*] Personal scheduler stopped")

    def get_status(self):
        """Get scheduler status."""
        jobs = self.scheduler.get_jobs()
        return {
            "running": self.scheduler.running,
            "pending_jobs": len(jobs),
            "today_posts": self.today_posts,
            "queue_size": len(self.post_queue),
        }
