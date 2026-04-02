"""
Auto Post - GitHub Actions Facebook Poster
=============================================
Uses date + hour to pick the right post.
No state file needed - deterministic based on time.
No duplicate posts within the same day.
"""

import os
import sys
import random
import logging
import requests
import feedparser
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from posts import POSTS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("AutoPost")

FB_TOKEN = os.getenv("FB_ACCESS_TOKEN", "")
FB_PERSONAL_PAGE_ID = os.getenv("FB_PERSONAL_PAGE_ID", "")
FB_GRAPH_URL = "https://graph.facebook.com/v25.0"

# Bangladesh timezone (UTC+6)
BDT = timezone(timedelta(hours=6))


def get_page_token(page_id):
    try:
        url = f"{FB_GRAPH_URL}/{page_id}?fields=access_token&access_token={FB_TOKEN}"
        r = requests.get(url)
        data = r.json()
        if "access_token" in data:
            return data["access_token"]
    except:
        pass
    return FB_TOKEN


def post_to_fb(page_id, message):
    token = get_page_token(page_id)
    url = f"{FB_GRAPH_URL}/{page_id}/feed"
    r = requests.post(url, data={"access_token": token, "message": message})
    result = r.json()
    if "id" in result:
        logger.info(f"[+] Posted! ID: {result['id']}")
        return True
    else:
        logger.error(f"[!] Failed: {result}")
        return False


def get_recent_posts():
    """Check what was posted recently to avoid duplicates."""
    try:
        token = get_page_token(FB_PERSONAL_PAGE_ID)
        url = f"{FB_GRAPH_URL}/{FB_PERSONAL_PAGE_ID}/feed"
        params = {"access_token": token, "fields": "message", "limit": 15}
        r = requests.get(url, params=params)
        data = r.json()
        if "data" in data:
            return [p.get("message", "")[:80] for p in data["data"]]
    except:
        pass
    return []


# ============ AI News ============

AI_NEWS_FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.artificialintelligence-news.com/feed/",
    "https://openai.com/blog/rss/",
    "https://blog.google/technology/ai/rss/",
    "https://www.wired.com/feed/tag/ai/latest/rss",
]

HOOKS = [
    "BREAKING: {title}\n\nThis changes everything.",
    "You need to know about this.\n\n{title}",
    "This is HUGE for anyone in tech.\n\n{title}",
    "Stop scrolling. Read this.\n\n{title}",
    "Everyone is talking about this today.\n\n{title}",
    "Most people will miss this. Don't be most people.\n\n{title}",
]


def get_ai_news_post():
    for feed_url in AI_NEWS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            if feed.entries:
                entry = random.choice(feed.entries[:5])
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                if summary:
                    soup = BeautifulSoup(summary, "html.parser")
                    summary = soup.get_text()[:300]
                hook = random.choice(HOOKS).format(title=title)
                return (
                    f"{hook}\n\n"
                    f"{summary}\n\n"
                    f"What do you think? Comment below.\n\n"
                    f"Follow Inzamul Haque for daily AI updates.\n\n"
                    f"#AI #TechNews #ArtificialIntelligence"
                )
        except:
            continue
    return None


# ============ Main ============

def main():
    if not FB_TOKEN or not FB_PERSONAL_PAGE_ID:
        logger.error("[!] Missing env vars")
        sys.exit(1)

    now = datetime.now(BDT)
    day_of_year = now.timetuple().tm_yday  # 1-366
    hour = now.hour

    # Calculate which post slot this is (10 posts/day)
    # Map hours to slots: 7,9,10,12,13,15,17,19,21,22
    slot_hours = [7, 9, 10, 12, 13, 15, 17, 19, 21, 22]

    # Find closest slot
    slot = 0
    for i, h in enumerate(slot_hours):
        if hour >= h:
            slot = i

    # Post index = (day * 10 + slot) mod total posts
    post_index = ((day_of_year - 1) * 10 + slot) % len(POSTS)

    logger.info(f"[*] Day {day_of_year}, Hour {hour}, Slot {slot}, Post index {post_index}")

    # Check recent posts to avoid duplicates
    recent = get_recent_posts()
    selected_post = POSTS[post_index]
    first_line = selected_post.split('\n')[0][:60]

    # If this post was already posted recently, use AI news instead
    is_duplicate = any(first_line in r for r in recent)

    if is_duplicate:
        logger.info("[*] Post already posted recently, using AI news instead")
        post = get_ai_news_post()
        if not post:
            # Try next post in list
            post_index = (post_index + 1) % len(POSTS)
            post = POSTS[post_index]
    elif slot % 3 == 0:
        # Every 3rd slot = AI news
        logger.info("[*] AI news slot")
        post = get_ai_news_post()
        if not post:
            post = selected_post
    else:
        post = selected_post

    logger.info(f"[*] Posting: {post[:80]}...")

    success = post_to_fb(FB_PERSONAL_PAGE_ID, post)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
