"""
News Auto Poster - Full Pipeline
==================================
Orchestrates: Scrape → Caption → Image → Post to FB

Runs continuously, checks for new articles periodically.
"""

import os
import sys
import time
import logging
import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from news.scraper import get_latest_news, scrape_article_detail, download_image, mark_posted
from news.caption_gen import generate_caption
from news.image_maker import create_news_image

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("NewsPoster")

# Lock file to prevent multiple instances
LOCK_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "news", "poster.lock")


def acquire_lock():
    """Prevent multiple instances from running."""
    if os.path.exists(LOCK_FILE):
        # Check if lock is stale (older than 30 min)
        age = time.time() - os.path.getmtime(LOCK_FILE)
        if age < 1800:
            logger.error("[!] Another instance is already running! Exiting.")
            sys.exit(1)
        else:
            logger.warning("[!] Stale lock found, removing...")
    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))


def release_lock():
    """Remove lock file."""
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

# Config
FB_TOKEN = os.getenv("FB_ACCESS_TOKEN", "")
FB_NEWS_PAGE_ID = os.getenv("FB_NEWS_PAGE_ID", "")
FB_GRAPH_URL = "https://graph.facebook.com/v25.0"
BDT = timezone(timedelta(hours=6))

# Temp directory for downloaded images
TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "news", "temp")

# Safe posting limits
POST_DELAY = 120        # 2 minutes gap between posts
CHECK_INTERVAL = 1800   # Check every 30 minutes
MAX_PER_CYCLE = 1       # 1 post per cycle
MAX_PER_DAY = 45        # Daily limit (~2 per hour safe)


def get_page_token(page_id):
    """Get page-specific access token."""
    try:
        url = f"{FB_GRAPH_URL}/{page_id}?fields=access_token&access_token={FB_TOKEN}"
        r = requests.get(url)
        data = r.json()
        if "access_token" in data:
            return data["access_token"]
    except Exception:
        pass
    return FB_TOKEN


def post_image_to_fb(image_path, caption):
    """Post an image with caption to the news FB page."""
    token = get_page_token(FB_NEWS_PAGE_ID)
    url = f"{FB_GRAPH_URL}/{FB_NEWS_PAGE_ID}/photos"

    with open(image_path, "rb") as f:
        files = {"source": f}
        data = {
            "access_token": token,
            "message": caption,
        }
        response = requests.post(url, data=data, files=files)

    result = response.json()
    if "id" in result:
        logger.info(f"[+] Posted to FB! ID: {result['id']}")
        return True
    else:
        logger.error(f"[!] FB post failed: {result}")
        return False


def process_article(article):
    """
    Process a single article through the full pipeline.
    Scrape detail → Download image → Generate caption → Create template → Post
    """
    article_id = article["article_id"]

    # Double-check not already posted (prevents race condition)
    from news.scraper import load_posted
    if article_id in load_posted():
        logger.info(f"[*] Skipping {article_id} - already posted")
        return False

    logger.info(f"\n{'='*50}")
    logger.info(f"[*] Processing: {article['title'][:60]}...")

    # Step 1: Get full article details
    detail = scrape_article_detail(article["url"])
    if not detail:
        logger.error(f"[!] Could not scrape article detail: {article['url']}")
        return False

    title = detail["title"]
    summary = detail.get("summary", "")
    image_url = detail.get("image_url", "")
    category = article.get("category", "national")

    # Step 2: Download news image
    news_image_path = None
    if image_url and "placeholder" not in image_url:
        news_image_path = download_image(image_url, TEMP_DIR)

    # Step 3: Generate AI caption
    caption = generate_caption(title, summary, category)
    logger.info(f"[*] Caption: {caption[:100]}...")

    # Step 4: Create template image
    template_path = create_news_image(
        title=title,
        news_image_path=news_image_path,
        article_id=article_id,
        summary=summary,
    )

    if not template_path or not os.path.exists(template_path):
        logger.error("[!] Failed to create template image")
        return False

    # Step 5: Post to Facebook
    success = post_image_to_fb(template_path, caption)

    if success:
        mark_posted(article_id)
        logger.info(f"[+] Article {article_id} posted successfully!")

        # Clean up ALL images - temp + template
        for path in [news_image_path, template_path]:
            if path and os.path.exists(path):
                os.remove(path)
                logger.info(f"[*] Deleted: {os.path.basename(path)}")

        # Also clean cropped versions
        if news_image_path:
            cropped = news_image_path.rsplit(".", 1)[0] + "_cropped.jpg"
            if os.path.exists(cropped):
                os.remove(cropped)
    else:
        logger.error(f"[!] Failed to post article {article_id}")

    return success


def run_once(limit=None):
    """Run one cycle: fetch new articles and post them."""
    if not FB_TOKEN or not FB_NEWS_PAGE_ID:
        logger.error("[!] Missing FB_ACCESS_TOKEN or FB_NEWS_PAGE_ID in .env")
        return 0

    if limit is None:
        limit = MAX_PER_CYCLE

    logger.info(f"\n{'='*60}")
    logger.info(f"[*] Starting news cycle at {datetime.now(BDT).strftime('%Y-%m-%d %H:%M:%S BDT')}")

    # Get latest unposted news
    articles = get_latest_news(limit=limit)

    if not articles:
        logger.info("[*] No new articles to post")
        return 0

    logger.info(f"[*] Found {len(articles)} new articles (max {limit} per cycle)")

    posted_count = 0
    for article in articles:
        success = process_article(article)
        if success:
            posted_count += 1
            # Delay between posts
            if posted_count < len(articles):
                logger.info(f"[*] Waiting {POST_DELAY}s before next post...")
                time.sleep(POST_DELAY)

    logger.info(f"\n[+] Cycle complete: {posted_count}/{len(articles)} posted")
    return posted_count


def run_continuous():
    """Run continuously with safe daily limits."""
    acquire_lock()
    try:
        _run_continuous_loop()
    finally:
        release_lock()


def _run_continuous_loop():
    logger.info("[*] ============================================")
    logger.info("[*]  দেশের খবর - Desher Khobor Auto Poster")
    logger.info("[*] ============================================")
    logger.info(f"[*] Check every: {CHECK_INTERVAL//60} min | Max per cycle: {MAX_PER_CYCLE} | Daily limit: {MAX_PER_DAY}")
    logger.info(f"[*] Post delay: {POST_DELAY}s between posts")

    daily_count = 0
    current_day = datetime.now(BDT).date()

    while True:
        now = datetime.now(BDT)

        # Reset daily counter at midnight
        if now.date() != current_day:
            logger.info(f"\n[*] New day! Resetting daily counter (yesterday: {daily_count} posts)")
            daily_count = 0
            current_day = now.date()

        # Check daily limit
        if daily_count >= MAX_PER_DAY:
            logger.info(f"[*] Daily limit reached ({MAX_PER_DAY}). Waiting for next day...")
            time.sleep(CHECK_INTERVAL)
            continue

        remaining = MAX_PER_DAY - daily_count
        cycle_limit = min(MAX_PER_CYCLE, remaining)

        try:
            posted = run_once(limit=cycle_limit)
            daily_count += posted
            logger.info(f"[*] Today's total: {daily_count}/{MAX_PER_DAY}")
        except Exception as e:
            logger.error(f"[!] Error in cycle: {e}")

        logger.info(f"[*] Next check in {CHECK_INTERVAL//60} min...")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Desher Khobor - News Auto Poster")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--limit", type=int, default=5, help="Max articles per cycle")
    parser.add_argument("--continuous", action="store_true", help="Run continuously")
    args = parser.parse_args()

    if args.once:
        run_once(limit=args.limit)
    elif args.continuous:
        run_continuous()
    else:
        # Default: run once
        run_once(limit=args.limit)
