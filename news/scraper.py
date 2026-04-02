"""
Jagonews24 News Scraper
========================
Scrapes latest news articles from jagonews24.com
Gets title, image, summary, category, date.
"""

import os
import json
import logging
import requests
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logger = logging.getLogger("NewsScraper")

BASE_URL = "https://www.jagonews24.com"
CDN_URL = "https://cdn.jagonews24.com"

# Categories to scrape
CATEGORIES = [
    "/national",
    "/politics",
    "/economy",
    "/international",
    "/sports",
    "/entertainment",
    "/country",
]

# BDT timezone
BDT = timezone(timedelta(hours=6))

# Track posted articles to avoid duplicates
POSTED_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "news", "posted.json")


def load_posted():
    """Load list of already posted article IDs."""
    if os.path.exists(POSTED_FILE):
        with open(POSTED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_posted(posted_ids):
    """Save posted article IDs."""
    os.makedirs(os.path.dirname(POSTED_FILE), exist_ok=True)
    # Keep only last 500 IDs to prevent file from growing too large
    posted_ids = posted_ids[-500:]
    with open(POSTED_FILE, "w", encoding="utf-8") as f:
        json.dump(posted_ids, f)


def mark_posted(article_id):
    """Mark an article as posted."""
    posted = load_posted()
    if article_id not in posted:
        posted.append(article_id)
        save_posted(posted)


def get_article_id(url):
    """Extract article ID from URL like /national/news/1106946."""
    parts = url.rstrip("/").split("/")
    return parts[-1] if parts else ""


def fetch_page(url):
    """Fetch a page with proper headers."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "bn-BD,bn;q=0.9,en;q=0.8",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logger.error(f"[!] Failed to fetch {url}: {e}")
        return None


def scrape_article_list(category="/national"):
    """
    Scrape list of articles from a category page.
    Returns list of dicts: {url, title, article_id}
    """
    url = f"{BASE_URL}{category}"
    html = fetch_page(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    articles = []
    seen_ids = set()

    # Find all article links (hrefs can be full URLs or relative)
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]

        # Match pattern: contains /news/ and ends with a number
        if "/news/" not in href:
            continue

        full_url = href if href.startswith("http") else urljoin(BASE_URL, href)
        article_id = get_article_id(full_url)

        if not article_id or not article_id.isdigit():
            continue
        if article_id in seen_ids:
            continue
        seen_ids.add(article_id)

        # Get title: from text, title attribute, or img alt
        title = a_tag.get_text(strip=True)
        if not title or len(title) < 5:
            title = a_tag.get("title", "")
        if not title or len(title) < 5:
            img = a_tag.find("img")
            if img:
                title = img.get("alt", "")
        if not title or len(title) < 5:
            continue

        articles.append({
            "url": full_url,
            "title": title,
            "article_id": article_id,
            "category": category.strip("/"),
        })

    logger.info(f"[+] Found {len(articles)} articles from {category}")
    return articles


def scrape_article_detail(article_url):
    """
    Scrape full article details from article page.
    Returns: {title, image_url, summary, author, date, category}
    """
    html = fetch_page(article_url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    # Title - from h1 or og:title
    title = ""
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True)
    if not title:
        og_title = soup.find("meta", property="og:title")
        if og_title:
            title = og_title.get("content", "")

    # Image - from og:image or first large image in article
    image_url = ""
    og_image = soup.find("meta", property="og:image")
    if og_image:
        image_url = og_image.get("content", "")

    if not image_url or "placeholder" in image_url:
        # Find first large image in article body
        for img in soup.find_all("img", src=True):
            src = img["src"]
            if "cdn.jagonews24.com" in src and "placeholder" not in src:
                image_url = src
                break

    if not image_url or "placeholder" in image_url:
        # Try data-src for lazy loaded images
        for img in soup.find_all("img", attrs={"data-src": True}):
            src = img["data-src"]
            if "placeholder" not in src:
                image_url = src
                break

    # Summary - first 2-3 paragraphs
    summary = ""
    article_body = soup.find("div", class_="newsDtlBodyContent") or soup.find("div", class_="news-detail-body")
    if article_body:
        paragraphs = article_body.find_all("p")
        summary = " ".join(p.get_text(strip=True) for p in paragraphs[:3])
    if not summary:
        og_desc = soup.find("meta", property="og:description")
        if og_desc:
            summary = og_desc.get("content", "")

    # Author
    author = ""
    author_el = soup.find("span", class_="author") or soup.find("a", class_="author")
    if author_el:
        author = author_el.get_text(strip=True)

    # Date
    date = ""
    time_el = soup.find("time")
    if time_el:
        date = time_el.get_text(strip=True)
    if not date:
        date_el = soup.find("span", class_="date") or soup.find("div", class_="date")
        if date_el:
            date = date_el.get_text(strip=True)

    if not title:
        return None

    return {
        "title": title,
        "image_url": image_url,
        "summary": summary[:500],
        "author": author,
        "date": date,
        "url": article_url,
    }


def download_image(image_url, save_dir):
    """Download image and return local path."""
    if not image_url:
        return None

    os.makedirs(save_dir, exist_ok=True)
    filename = image_url.split("/")[-1].split("?")[0]
    if not filename:
        filename = "news_image.jpg"

    save_path = os.path.join(save_dir, filename)

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": BASE_URL,
        }
        resp = requests.get(image_url, headers=headers, timeout=15)
        resp.raise_for_status()

        with open(save_path, "wb") as f:
            f.write(resp.content)

        logger.info(f"[+] Image saved: {save_path}")
        return save_path
    except Exception as e:
        logger.error(f"[!] Image download failed: {e}")
        return None


def get_latest_news(categories=None, limit=20):
    """
    Get latest news from all categories, excluding already posted.
    Returns list of article dicts with full details.
    """
    if categories is None:
        categories = CATEGORIES

    posted = load_posted()
    all_articles = []

    for cat in categories:
        articles = scrape_article_list(cat)
        for article in articles:
            if article["article_id"] not in posted:
                all_articles.append(article)

    # Remove duplicates by article_id
    seen = set()
    unique = []
    for a in all_articles:
        if a["article_id"] not in seen:
            seen.add(a["article_id"])
            unique.append(a)

    # Limit
    unique = unique[:limit]

    logger.info(f"[+] {len(unique)} new articles to process")
    return unique


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

    print("=== Scraping latest news ===")
    articles = get_latest_news(categories=["/national"], limit=5)

    for i, article in enumerate(articles):
        print(f"\n--- Article {i+1} ---")
        print(f"Title: {article['title']}")
        print(f"URL: {article['url']}")

        detail = scrape_article_detail(article["url"])
        if detail:
            print(f"Image: {detail['image_url']}")
            print(f"Summary: {detail['summary'][:200]}...")
