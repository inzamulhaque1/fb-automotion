"""
Auto Post - Lightweight script for GitHub Actions
====================================================
Runs every 90 min via cron.
Posts in order (no repeats) + AI news mixed in.
"""

import os
import sys
import json
import random
import logging
import requests
import feedparser
from bs4 import BeautifulSoup
from posts import POSTS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("AutoPost")

# Config from environment variables
FB_TOKEN = os.getenv("FB_ACCESS_TOKEN", "")
FB_PERSONAL_PAGE_ID = os.getenv("FB_PERSONAL_PAGE_ID", "")

FB_GRAPH_URL = "https://graph.facebook.com/v25.0"
STATE_FILE = "post_state.json"


# ============ State Management ============

def load_state():
    """Load which post index we're on."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"index": 0, "posted_count": 0}


def save_state(state):
    """Save current post index."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


# ============ Facebook API ============

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
    "If you're not paying attention to this, you're falling behind.\n\n{title}",
    "Most people will miss this. Don't be most people.\n\n{title}",
]


def get_ai_news_post():
    """Fetch real AI news and format as post."""
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
                post = (
                    f"{hook}\n\n"
                    f"{summary}\n\n"
                    f"What do you think about this? Comment below.\n\n"
                    f"Follow Inzamul Haque for daily AI updates.\n\n"
                    f"#AI #TechNews #ArtificialIntelligence"
                )
                return post
        except:
            continue
    return None


# ============ Main ============

def main():
    if not FB_TOKEN or not FB_PERSONAL_PAGE_ID:
        logger.error("[!] Missing env vars")
        sys.exit(1)

    state = load_state()
    index = state["index"]

    # Every 3rd post = AI news, rest = viral posts in order
    if (state["posted_count"] + 1) % 3 == 0:
        logger.info("[*] Generating AI news post...")
        post = get_ai_news_post()
        if not post:
            post = POSTS[index % len(POSTS)]
            index += 1
    else:
        logger.info(f"[*] Using post #{index + 1}/{len(POSTS)}...")
        post = POSTS[index % len(POSTS)]
        index += 1

    logger.info(f"[*] Post preview: {post[:80]}...")

    success = post_to_fb(FB_PERSONAL_PAGE_ID, post)

    if success:
        state["index"] = index
        state["posted_count"] = state["posted_count"] + 1
        save_state(state)
        logger.info(f"[+] Done! Total posted: {state['posted_count']}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
