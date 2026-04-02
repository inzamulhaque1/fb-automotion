"""
AI News & Trends - Influencer-style posts
============================================
Breaking AI news with engaging hooks like top tech influencers.
"""

import logging
import random
import feedparser
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger("AINews")

AI_NEWS_FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.artificialintelligence-news.com/feed/",
    "https://openai.com/blog/rss/",
    "https://blog.google/technology/ai/rss/",
    "https://www.wired.com/feed/tag/ai/latest/rss",
    "https://feeds.feedburner.com/TheHackersNews",
]

# Engaging hook templates (like Rene Remsik, Awa K. Penn style)
HOOKS = [
    "BREAKING: {title}\n\nThis changes everything. Here's why:",
    "You need to know about this.\n\n{title}\n\nBookmark this before it's gone:",
    "This is HUGE for anyone in tech.\n\n{title}\n\nHere's the breakdown:",
    "Stop scrolling. Read this.\n\n{title}\n\nThis will impact how we build software:",
    "Everyone is talking about this today.\n\n{title}\n\nHere's what you need to know:",
    "If you're not paying attention to this, you're falling behind.\n\n{title}",
    "I can't believe this is happening in 2026.\n\n{title}\n\nLet me explain:",
    "This just dropped and the internet is going crazy.\n\n{title}",
    "Your job in tech is about to change because of this.\n\n{title}\n\nThread:",
    "Most people will miss this. Don't be most people.\n\n{title}",
]

OUTROS = [
    "\n\nFollow Inzamul Haque for daily AI updates.\nShare this if you found it useful.",
    "\n\nBookmark this post.\nFollow me for more AI breakdowns.",
    "\n\nDrop a comment with your thoughts.\nFollow for daily AI trends.",
    "\n\nShare this with someone who needs to see this.\nFollow Inzamul Haque for more.",
    "\n\nWhat do you think? Comment below.\nFollow me - I post AI updates daily.",
]

HASHTAGS = "#AI #ArtificialIntelligence #TechNews #AITools #MachineLearning #Tech2026"


def fetch_news(max_per_feed=3):
    """Fetch latest AI news from RSS feeds."""
    all_news = []
    for feed_url in AI_NEWS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            source = feed.feed.get("title", "Unknown")
            for entry in feed.entries[:max_per_feed]:
                summary = entry.get("summary", "")
                if summary:
                    soup = BeautifulSoup(summary, "html.parser")
                    summary = soup.get_text()[:500]
                all_news.append({
                    "title": entry.get("title", ""),
                    "summary": summary,
                    "link": entry.get("link", ""),
                    "source": source,
                })
        except Exception as e:
            logger.warning(f"[!] Failed to fetch {feed_url}: {e}")
    logger.info(f"[+] Fetched {len(all_news)} AI news articles")
    return all_news


def format_breaking_news(news_item):
    """Format as breaking news influencer post."""
    hook = random.choice(HOOKS).format(title=news_item["title"])
    outro = random.choice(OUTROS)

    post = (
        f"{hook}\n\n"
        f"{news_item['summary'][:300]}\n\n"
        f"Source: {news_item['source']}\n"
        f"Read more: {news_item['link']}"
        f"{outro}\n\n"
        f"{HASHTAGS}"
    )
    return post


def format_analysis_post(news_item):
    """Format as analysis/opinion post."""
    post = (
        f"Everyone's talking about this but nobody's explaining it properly.\n\n"
        f"{news_item['title']}\n\n"
        f"Here's my take:\n\n"
        f"{news_item['summary'][:400]}\n\n"
        f"Why this matters for YOU:\n"
        f"- If you're a developer, this changes how you build apps\n"
        f"- If you're in business, this is a competitive advantage\n"
        f"- If you're learning tech, focus on this NOW\n\n"
        f"Source: {news_item['link']}\n\n"
        f"Follow Inzamul Haque for daily AI analysis.\n\n"
        f"{HASHTAGS}"
    )
    return post


def get_news_posts(count=3):
    """Get influencer-style news posts."""
    news = fetch_news(max_per_feed=2)
    posts = []

    for i, item in enumerate(news[:count]):
        if i % 2 == 0:
            text = format_breaking_news(item)
        else:
            text = format_analysis_post(item)

        posts.append({
            "type": "ai_news",
            "text": text,
            "title": item["title"],
            "source": item["source"],
            "link": item["link"],
        })

    logger.info(f"[+] Generated {len(posts)} AI news posts")
    return posts
