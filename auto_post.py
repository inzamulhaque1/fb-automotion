"""
Auto Post - Lightweight script for GitHub Actions
====================================================
Runs every 1-2 hours via cron.
Generates 1 post → posts to FB → exits.
"""

import os
import sys
import random
import logging
import requests
import feedparser
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("AutoPost")

# Config from environment variables (GitHub Secrets)
FB_TOKEN = os.getenv("FB_ACCESS_TOKEN", "")
FB_PERSONAL_PAGE_ID = os.getenv("FB_PERSONAL_PAGE_ID", "")
FB_GAMING_PAGE_ID = os.getenv("FB_GAMING_PAGE_ID", "")

FB_GRAPH_URL = "https://graph.facebook.com/v25.0"

# ============ Facebook API ============

def get_page_token(page_id):
    """Get page token from user token."""
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
    """Post text to Facebook page."""
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


# ============ Content Generators ============

AI_NEWS_FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.artificialintelligence-news.com/feed/",
    "https://openai.com/blog/rss/",
    "https://blog.google/technology/ai/rss/",
    "https://www.wired.com/feed/tag/ai/latest/rss",
]

HOOKS = [
    "BREAKING: {title}\n\nThis changes everything.",
    "You need to know about this.\n\n{title}\n\nBookmark this before it's gone.",
    "This is HUGE for anyone in tech.\n\n{title}",
    "Stop scrolling. Read this.\n\n{title}",
    "Everyone is talking about this today.\n\n{title}",
    "If you're not paying attention to this, you're falling behind.\n\n{title}",
    "Most people will miss this. Don't be most people.\n\n{title}",
]

VIRAL_POSTS = [
    (
        "Stop paying for software. These 7 FREE AI tools do the same job:\n\n"
        "1. ChatGPT + Claude - Replace your copywriter\n"
        "2. Canva AI - Replace your designer\n"
        "3. Gamma.app - Replace your presentation tool\n"
        "4. Descript - Replace your video editor\n"
        "5. Notion AI - Replace your project manager\n"
        "6. Perplexity - Replace your research assistant\n"
        "7. v0.dev - Replace your UI developer\n\n"
        "Total saved: $500+/month\nTotal cost: $0\n\n"
        "Save this post. You'll need it.\n\n"
        "Follow Inzamul Haque for more AI hacks.\n\n"
        "#AI #AITools #FreeTools #Productivity"
    ),
    (
        "5 AI side hustles making people $3000+/month in 2026:\n\n"
        "1. AI Content Agency - $500-2000/client\n"
        "2. AI Thumbnail Design - $20-50/thumbnail\n"
        "3. AI Chatbot Builder - $500-1500/bot\n"
        "4. AI Course Creator - Passive income\n"
        "5. AI Automation Consultant - $1000-3000/project\n\n"
        "The best time to start was yesterday.\n"
        "The second best time is NOW.\n\n"
        "Follow Inzamul Haque for more AI money tips.\n\n"
        "#AI #SideHustle #MakeMoneyOnline"
    ),
    (
        "I tested Claude vs ChatGPT vs Gemini for a week.\n\n"
        "CLAUDE: Best for coding & writing (9/10)\n"
        "CHATGPT: Best all-rounder (8/10)\n"
        "GEMINI: Best for Google users (8/10)\n\n"
        "My recommendation:\n"
        "Use Claude for work. ChatGPT for creativity. Gemini for research.\n\n"
        "Agree or disagree? Comment below.\n\n"
        "Follow Inzamul Haque\n\n"
        "#AI #ChatGPT #Claude #Gemini"
    ),
    (
        "10 AI websites that will make you 10x more productive:\n\n"
        "1. perplexity.ai - AI search\n"
        "2. gamma.app - Presentations in seconds\n"
        "3. claude.ai - Best AI for coding\n"
        "4. v0.dev - Generate UI from text\n"
        "5. ideogram.ai - Free image generation\n"
        "6. notebooklm.google - AI research\n"
        "7. suno.ai - Create music with AI\n"
        "8. descript.com - Edit video like text\n"
        "9. heygen.com - AI video avatars\n"
        "10. replit.com - Build apps without coding\n\n"
        "Bookmark this post.\n\n"
        "Follow Inzamul Haque for daily AI tools.\n\n"
        "#AI #AITools #Productivity #Tech"
    ),
    (
        "Unpopular opinion: You don't need a CS degree in 2026.\n\n"
        "Here's what you need instead:\n\n"
        "1. Learn to use AI tools\n"
        "2. Build 5 real projects\n"
        "3. Learn prompt engineering\n"
        "4. Understand APIs\n"
        "5. Build an online presence\n\n"
        "Companies don't care about your degree.\n"
        "They care about what you can BUILD.\n\n"
        "Follow Inzamul Haque for real tech advice.\n\n"
        "#Tech #Career #NoDegree #AI"
    ),
    (
        "AI will NOT replace you.\nBut someone using AI WILL.\n\n"
        "Think about it:\n"
        "- A designer using AI creates 10x more designs\n"
        "- A developer using AI writes code 5x faster\n"
        "- A marketer using AI runs campaigns 3x more efficiently\n\n"
        "3 things you should do TODAY:\n"
        "1. Sign up for Claude or ChatGPT\n"
        "2. Use AI for your daily work\n"
        "3. Learn prompt engineering\n\n"
        "The future belongs to people who work WITH AI.\n\n"
        "Follow Inzamul Haque\n\n"
        "#AI #FutureOfWork #Productivity"
    ),
    (
        "5 FREE AI courses better than any $2000 bootcamp:\n\n"
        "1. DeepLearning.AI - Andrew Ng (Coursera)\n"
        "2. fast.ai - Practical Deep Learning\n"
        "3. Google AI Essentials - Certificate included\n"
        "4. Microsoft AI Fundamentals\n"
        "5. Hugging Face NLP Course\n\n"
        "Total cost: $0\nTotal value: Priceless\n\n"
        "Save this post. Start learning today.\n\n"
        "Follow Inzamul Haque\n\n"
        "#AI #FreeCourses #Learning #Education"
    ),
    (
        "আমি ২০২৬ সালে কোনো সফটওয়্যারের জন্য টাকা খরচ করি না।\n\n"
        "সব FREE AI টুলস দিয়ে করি।\n\n"
        "লেখালেখি: Claude AI, Notion AI\n"
        "ডিজাইন: Canva AI, Ideogram\n"
        "ভিডিও: CapCut, Descript\n"
        "রিসার্চ: Perplexity, NotebookLM\n"
        "কোডিং: Cursor, Replit\n\n"
        "মাসিক সাশ্রয়: $500+\nমোট খরচ: $0\n\n"
        "এই পোস্টটা সেভ করে রাখুন।\n\n"
        "Inzamul Haque ফলো করুন।\n\n"
        "#AI #বাংলা #FreeTools #Tech"
    ),
    (
        "এই ৫টি AI টুল না জানলে আপনি পিছিয়ে পড়বেন:\n\n"
        "১. Claude AI - কোডিং আর লেখালেখির জন্য সেরা\n"
        "২. Perplexity AI - Google এর বিকল্প\n"
        "৩. Gamma App - ৩০ সেকেন্ডে প্রেজেন্টেশন\n"
        "৪. v0.dev - কোডিং ছাড়াই ওয়েবসাইট\n"
        "৫. Suno AI - AI দিয়ে গান বানান\n\n"
        "এই ৫টি টুল শিখে নিন - ক্যারিয়ার বদলে যাবে।\n\n"
        "Inzamul Haque ফলো করুন।\n\n"
        "#AI #বাংলা #AITools #Tech"
    ),
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
                link = entry.get("link", "")
                source = feed.feed.get("title", "")

                hook = random.choice(HOOKS).format(title=title)
                post = (
                    f"{hook}\n\n"
                    f"{summary}\n\n"
                    f"Source: {source}\n"
                    f"Read more: {link}\n\n"
                    f"Follow Inzamul Haque for daily AI updates.\n\n"
                    f"#AI #TechNews #ArtificialIntelligence"
                )
                return post
        except:
            continue
    return None


def get_viral_post():
    """Get a random viral-style post."""
    return random.choice(VIRAL_POSTS)


# ============ Main ============

def main():
    if not FB_TOKEN or not FB_PERSONAL_PAGE_ID:
        logger.error("[!] Missing FB_ACCESS_TOKEN or FB_PERSONAL_PAGE_ID env vars")
        sys.exit(1)

    # Randomly choose: AI news (40%) or viral post (60%)
    roll = random.random()

    if roll < 0.4:
        logger.info("[*] Generating AI news post...")
        post = get_ai_news_post()
        if not post:
            logger.warning("[!] News fetch failed, using viral post")
            post = get_viral_post()
    else:
        logger.info("[*] Using viral post...")
        post = get_viral_post()

    logger.info(f"[*] Post preview: {post[:100]}...")

    # Post to personal page
    success = post_to_fb(FB_PERSONAL_PAGE_ID, post)

    if success:
        logger.info("[+] Successfully posted to Inzamul Haque page!")
    else:
        logger.error("[!] Failed to post")
        sys.exit(1)


if __name__ == "__main__":
    main()
