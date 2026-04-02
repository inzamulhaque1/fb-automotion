"""
ArenaHype Auto Poster - Full Pipeline
=======================================
Orchestrates: Scrape → Caption → Image → Post to FB

Handles both:
1. Football news articles (news template)
2. Match results (scoreboard template)
"""

import os
import sys
import time
import logging
import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sports.scraper import (
    get_latest_football_news, get_latest_match_results,
    get_article_detail, download_image, mark_posted,
)
from sports.caption_gen import generate_news_caption, generate_match_caption
from sports.image_maker import create_news_image, create_match_result_image

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("SportsPostr")

# Config
FB_TOKEN = os.getenv("FB_ACCESS_TOKEN", "")
FB_SPORTS_PAGE_ID = os.getenv("FB_SPORTS_PAGE_ID", "")
FB_GRAPH_URL = "https://graph.facebook.com/v25.0"

TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "sports", "temp")

# Safe posting limits
POST_DELAY = 120        # 2 minutes between posts
CHECK_INTERVAL = 1800   # Check every 30 minutes
MAX_NEWS_PER_CYCLE = 1  # 1 news post per cycle
MAX_MATCH_PER_CYCLE = 2 # 2 match results per cycle
MAX_PER_DAY = 30        # Daily limit


def get_page_token(page_id):
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
    """Post an image with caption to the ArenaHype FB page."""
    token = get_page_token(FB_SPORTS_PAGE_ID)
    url = f"{FB_GRAPH_URL}/{FB_SPORTS_PAGE_ID}/photos"

    with open(image_path, "rb") as f:
        files = {"source": f}
        data = {
            "access_token": token,
            "message": caption,
        }
        response = requests.post(url, data=data, files=files)

    result = response.json()
    if "id" in result:
        logger.info(f"[+] Posted to ArenaHype! ID: {result['id']}")
        return True
    else:
        logger.error(f"[!] FB post failed: {result}")
        return False


def cleanup_files(*paths):
    """Clean up temp files."""
    for path in paths:
        if path and os.path.exists(path):
            try:
                os.remove(path)
                logger.info(f"[*] Deleted: {os.path.basename(path)}")
            except Exception:
                pass


def process_news_article(article):
    """Process a news article through the full pipeline."""
    article_id = article["article_id"]
    logger.info(f"\n{'='*50}")
    logger.info(f"[*] Processing news: {article['title'][:60]}...")

    # Step 1: Get full article details
    detail = get_article_detail(article)
    if not detail:
        logger.error(f"[!] Could not get article detail")
        return False

    title = detail["title"]
    summary = detail.get("summary", "")
    image_url = detail.get("image_url", "")
    source = detail.get("source", article.get("source", ""))

    # Step 2: Download news image
    news_image_path = None
    if image_url:
        news_image_path = download_image(image_url, TEMP_DIR)

    # Step 3: Generate AI caption
    caption = generate_news_caption(title, summary, source)
    logger.info(f"[*] Caption: {caption[:100]}...")

    # Step 4: Create template image (NEWS template)
    template_path = create_news_image(
        title=title,
        news_image_path=news_image_path,
        article_id=article_id,
        summary=summary,
        source=source,
    )

    if not template_path or not os.path.exists(template_path):
        logger.error("[!] Failed to create news image")
        return False

    # Step 5: Post to Facebook
    success = post_image_to_fb(template_path, caption)

    if success:
        mark_posted(article_id)
        logger.info(f"[+] News article posted!")
        # Clean up
        cleanup_files(news_image_path, template_path)
        if news_image_path:
            cropped = news_image_path.rsplit(".", 1)[0] + "_cropped.jpg"
            cleanup_files(cropped)
    else:
        logger.error(f"[!] Failed to post news article")

    return success


def process_match_result(match):
    """Process a match result through the pipeline."""
    match_id = match["article_id"]
    home = match["home_team"]
    away = match["away_team"]
    h_score = match["home_score"]
    a_score = match["away_score"]
    competition = match.get("competition", "")
    status = match.get("status", "Full Time")

    logger.info(f"\n{'='*50}")
    logger.info(f"[*] Processing match: {home} {h_score} - {a_score} {away}")

    # Step 1: Generate AI caption
    caption = generate_match_caption(home, away, h_score, a_score, competition)
    logger.info(f"[*] Caption: {caption[:100]}...")

    # Step 2: Create MATCH RESULT template image (scoreboard)
    template_path = create_match_result_image(
        home_team=home,
        away_team=away,
        home_score=h_score,
        away_score=a_score,
        competition=competition,
        status=status,
        match_id=match_id,
    )

    if not template_path or not os.path.exists(template_path):
        logger.error("[!] Failed to create match result image")
        return False

    # Step 3: Post to Facebook
    success = post_image_to_fb(template_path, caption)

    if success:
        mark_posted(match_id)
        logger.info(f"[+] Match result posted!")
        cleanup_files(template_path)
    else:
        logger.error(f"[!] Failed to post match result")

    return success


def run_once(news_limit=None, match_limit=None):
    """Run one cycle: fetch & post news + match results."""
    if not FB_TOKEN or not FB_SPORTS_PAGE_ID:
        logger.error("[!] Missing FB_ACCESS_TOKEN or FB_SPORTS_PAGE_ID in .env")
        return 0

    if news_limit is None:
        news_limit = MAX_NEWS_PER_CYCLE
    if match_limit is None:
        match_limit = MAX_MATCH_PER_CYCLE

    logger.info(f"\n{'='*60}")
    logger.info(f"[*] ArenaHype cycle at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")

    posted_count = 0

    # --- NEWS ARTICLES ---
    articles = get_latest_football_news(limit=news_limit)
    if articles:
        logger.info(f"[*] {len(articles)} new football articles")
        for article in articles:
            success = process_news_article(article)
            if success:
                posted_count += 1
                time.sleep(POST_DELAY)
    else:
        logger.info("[*] No new articles")

    # --- MATCH RESULTS ---
    matches = get_latest_match_results()
    if matches:
        matches = matches[:match_limit]
        logger.info(f"[*] {len(matches)} new match results")
        for match in matches:
            success = process_match_result(match)
            if success:
                posted_count += 1
                time.sleep(POST_DELAY)
    else:
        logger.info("[*] No new match results")

    logger.info(f"\n[+] Cycle complete: {posted_count} posted")
    return posted_count


def run_continuous():
    """Run continuously with safe daily limits."""
    logger.info("[*] ============================================")
    logger.info("[*]  ⚽ ArenaHype - Football Auto Poster")
    logger.info("[*] ============================================")
    logger.info(f"[*] Check every: {CHECK_INTERVAL//60} min | Daily limit: {MAX_PER_DAY}")

    daily_count = 0
    current_day = datetime.now(timezone.utc).date()

    while True:
        now = datetime.now(timezone.utc)

        if now.date() != current_day:
            logger.info(f"\n[*] New day! Yesterday: {daily_count} posts")
            daily_count = 0
            current_day = now.date()

        if daily_count >= MAX_PER_DAY:
            logger.info(f"[*] Daily limit reached ({MAX_PER_DAY}). Waiting...")
            time.sleep(CHECK_INTERVAL)
            continue

        try:
            posted = run_once()
            daily_count += posted
            logger.info(f"[*] Today: {daily_count}/{MAX_PER_DAY}")
        except Exception as e:
            logger.error(f"[!] Error: {e}")

        logger.info(f"[*] Next check in {CHECK_INTERVAL//60} min...")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ArenaHype - Football Auto Poster")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--news-limit", type=int, default=3, help="Max news per cycle")
    parser.add_argument("--match-limit", type=int, default=3, help="Max match results per cycle")
    parser.add_argument("--continuous", action="store_true", help="Run continuously")
    parser.add_argument("--news-only", action="store_true", help="Only post news, no match results")
    parser.add_argument("--matches-only", action="store_true", help="Only post match results")
    args = parser.parse_args()

    if args.once:
        if args.news_only:
            run_once(news_limit=args.news_limit, match_limit=0)
        elif args.matches_only:
            run_once(news_limit=0, match_limit=args.match_limit)
        else:
            run_once(news_limit=args.news_limit, match_limit=args.match_limit)
    elif args.continuous:
        run_continuous()
    else:
        run_once(news_limit=args.news_limit, match_limit=args.match_limit)
