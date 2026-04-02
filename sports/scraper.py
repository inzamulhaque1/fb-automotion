"""
Football News Scraper - ArenaHype
==================================
Scrapes latest football news & match results from:
- goal.com
- espn.com/soccer
- bbc.com/sport/football
"""

import os
import json
import logging
import requests
import re
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logger = logging.getLogger("SportsScraper")

# Track posted articles
POSTED_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "sports", "posted.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def load_posted():
    if os.path.exists(POSTED_FILE):
        with open(POSTED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_posted(posted_ids):
    os.makedirs(os.path.dirname(POSTED_FILE), exist_ok=True)
    posted_ids = posted_ids[-500:]
    with open(POSTED_FILE, "w", encoding="utf-8") as f:
        json.dump(posted_ids, f)


def mark_posted(article_id):
    posted = load_posted()
    if article_id not in posted:
        posted.append(article_id)
        save_posted(posted)


def fetch_page(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logger.error(f"[!] Failed to fetch {url}: {e}")
        return None


def generate_article_id(url):
    """Generate a unique ID from URL."""
    # Remove protocol and common prefixes
    clean = url.replace("https://", "").replace("http://", "").replace("www.", "")
    # Use last meaningful path segments
    parts = [p for p in clean.split("/") if p and p not in ("sport", "football", "soccer", "story")]
    return "_".join(parts[-2:]) if len(parts) >= 2 else parts[-1] if parts else str(hash(url))


# ============================================================
# BBC Sport Football Scraper
# ============================================================

def scrape_bbc_football():
    """Scrape football news from BBC Sport."""
    url = "https://www.bbc.com/sport/football"
    html = fetch_page(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    articles = []
    seen = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]

        # Match football article URLs (must be articles or live reports)
        if "/sport/football/" not in href and "/sport/articles/" not in href:
            continue
        if href.endswith("/football") or href.endswith("/football/"):
            continue
        # Skip section/nav pages
        if any(skip in href for skip in ["/top-scorers", "/leagues-cups", "/fixtures", "/tables", "/gossip"]):
            continue

        full_url = href if href.startswith("http") else urljoin("https://www.bbc.com", href)
        article_id = generate_article_id(full_url)

        if article_id in seen:
            continue
        seen.add(article_id)

        # Get title from text content
        title = a_tag.get_text(strip=True)
        if not title or len(title) < 10:
            # Try heading inside the link
            h = a_tag.find(["h2", "h3", "span"])
            if h:
                title = h.get_text(strip=True)
        if not title or len(title) < 10:
            continue
        # Skip non-article links
        if any(skip in title.lower() for skip in ["live scores", "tables", "fixtures", "results", "gossip column", "top scorers", "leagues & cups", "leagues &amp; cups", "transfers"]):
            continue

        articles.append({
            "url": full_url,
            "title": title,
            "article_id": article_id,
            "source": "bbc",
            "type": "news",
        })

    logger.info(f"[+] BBC: Found {len(articles)} articles")
    return articles[:15]


def scrape_bbc_article(url):
    """Get full article details from BBC Sport."""
    html = fetch_page(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    title = ""
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True)

    image_url = ""
    og_image = soup.find("meta", property="og:image")
    if og_image:
        image_url = og_image.get("content", "")

    summary = ""
    og_desc = soup.find("meta", property="og:description")
    if og_desc:
        summary = og_desc.get("content", "")
    if not summary:
        paragraphs = soup.find_all("p")
        for p in paragraphs[:5]:
            text = p.get_text(strip=True)
            if len(text) > 50:
                summary = text
                break

    if not title:
        return None

    return {
        "title": title,
        "image_url": image_url,
        "summary": summary[:500],
        "source": "BBC Sport",
        "url": url,
    }


# ============================================================
# ESPN Football Scraper
# ============================================================

def scrape_espn_football():
    """Scrape football news from ESPN."""
    url = "https://www.espn.com/soccer/"
    html = fetch_page(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    articles = []
    seen = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]

        if "/story/" not in href and "/soccer/" not in href:
            continue
        if href.count("/") < 3:
            continue

        full_url = href if href.startswith("http") else urljoin("https://www.espn.com", href)
        if "/story/" not in full_url:
            continue

        article_id = generate_article_id(full_url)
        if article_id in seen:
            continue
        seen.add(article_id)

        title = a_tag.get_text(strip=True)
        if not title or len(title) < 10:
            h = a_tag.find(["h2", "h3", "span"])
            if h:
                title = h.get_text(strip=True)
        if not title or len(title) < 10:
            continue

        articles.append({
            "url": full_url,
            "title": title,
            "article_id": article_id,
            "source": "espn",
            "type": "news",
        })

    logger.info(f"[+] ESPN: Found {len(articles)} articles")
    return articles[:15]


def scrape_espn_article(url):
    """Get full article details from ESPN."""
    html = fetch_page(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    title = ""
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True)
    if not title:
        og_title = soup.find("meta", property="og:title")
        if og_title:
            title = og_title.get("content", "")

    image_url = ""
    og_image = soup.find("meta", property="og:image")
    if og_image:
        image_url = og_image.get("content", "")

    summary = ""
    og_desc = soup.find("meta", property="og:description")
    if og_desc:
        summary = og_desc.get("content", "")

    if not title:
        return None

    return {
        "title": title,
        "image_url": image_url,
        "summary": summary[:500],
        "source": "ESPN",
        "url": url,
    }


# ============================================================
# Goal.com Football Scraper
# ============================================================

def scrape_goal_football():
    """Scrape football news from Goal.com."""
    url = "https://www.goal.com/en/news"
    html = fetch_page(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    articles = []
    seen = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]

        if "/en/" not in href:
            continue
        if any(skip in href for skip in ["/live-scores", "/tables", "/fixtures"]):
            continue

        full_url = href if href.startswith("http") else urljoin("https://www.goal.com", href)
        article_id = generate_article_id(full_url)

        if article_id in seen:
            continue
        seen.add(article_id)

        title = a_tag.get_text(strip=True)
        if not title or len(title) < 10:
            h = a_tag.find(["h2", "h3", "span"])
            if h:
                title = h.get_text(strip=True)
        if not title or len(title) < 10:
            continue

        articles.append({
            "url": full_url,
            "title": title,
            "article_id": article_id,
            "source": "goal",
            "type": "news",
        })

    logger.info(f"[+] Goal: Found {len(articles)} articles")
    return articles[:15]


def scrape_goal_article(url):
    """Get full article details from Goal.com."""
    html = fetch_page(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    title = ""
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True)
    if not title:
        og_title = soup.find("meta", property="og:title")
        if og_title:
            title = og_title.get("content", "")

    image_url = ""
    og_image = soup.find("meta", property="og:image")
    if og_image:
        image_url = og_image.get("content", "")

    summary = ""
    og_desc = soup.find("meta", property="og:description")
    if og_desc:
        summary = og_desc.get("content", "")

    if not title:
        return None

    return {
        "title": title,
        "image_url": image_url,
        "summary": summary[:500],
        "source": "Goal.com",
        "url": url,
    }


# ============================================================
# Match Results Scraper (ESPN Scoreboard)
# ============================================================

def scrape_match_results():
    """Scrape recent match results from ESPN soccer scoreboard."""
    url = "https://www.espn.com/soccer/scoreboard"
    html = fetch_page(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    matches = []

    # ESPN uses ScoreboardPage data in script tags
    for script in soup.find_all("script"):
        text = script.string or ""
        if "espn.scoreboardData" in text or '"events"' in text:
            # Try to extract JSON data
            try:
                json_match = re.search(r'\{.*"events".*\}', text)
                if json_match:
                    data = json.loads(json_match.group())
                    events = data.get("events", [])
                    for event in events:
                        competitions = event.get("competitions", [{}])
                        for comp in competitions:
                            competitors = comp.get("competitors", [])
                            if len(competitors) >= 2:
                                home = competitors[0]
                                away = competitors[1]
                                match_data = {
                                    "home_team": home.get("team", {}).get("displayName", ""),
                                    "away_team": away.get("team", {}).get("displayName", ""),
                                    "home_score": home.get("score", "0"),
                                    "away_score": away.get("score", "0"),
                                    "competition": event.get("season", {}).get("type", {}).get("name", ""),
                                    "status": comp.get("status", {}).get("type", {}).get("description", ""),
                                    "article_id": f"match_{event.get('id', '')}",
                                    "type": "match_result",
                                    "source": "espn",
                                }
                                if match_data["home_team"] and match_data["away_team"]:
                                    matches.append(match_data)
            except (json.JSONDecodeError, AttributeError):
                continue

    # Fallback: parse HTML structure
    if not matches:
        for section in soup.find_all("section", class_=re.compile("scoreboard|Scoreboard")):
            teams = section.find_all(class_=re.compile("team|Team"))
            scores = section.find_all(class_=re.compile("score|Score"))
            if len(teams) >= 2 and len(scores) >= 2:
                match_data = {
                    "home_team": teams[0].get_text(strip=True),
                    "away_team": teams[1].get_text(strip=True),
                    "home_score": scores[0].get_text(strip=True),
                    "away_score": scores[1].get_text(strip=True),
                    "competition": "",
                    "status": "Full Time",
                    "article_id": f"match_{generate_article_id(teams[0].get_text(strip=True) + teams[1].get_text(strip=True))}",
                    "type": "match_result",
                    "source": "espn",
                }
                matches.append(match_data)

    logger.info(f"[+] Match Results: Found {len(matches)} matches")
    return matches


# ============================================================
# Unified Interface
# ============================================================

def get_article_detail(article):
    """Get full details for any article based on source."""
    source = article.get("source", "")
    url = article.get("url", "")

    if source == "bbc":
        return scrape_bbc_article(url)
    elif source == "espn":
        return scrape_espn_article(url)
    elif source == "goal":
        return scrape_goal_article(url)
    return None


def download_image(image_url, save_dir):
    """Download image and return local path."""
    if not image_url:
        return None

    os.makedirs(save_dir, exist_ok=True)
    filename = image_url.split("/")[-1].split("?")[0]
    if not filename or len(filename) > 100:
        filename = f"sports_{datetime.now().strftime('%H%M%S')}.jpg"

    save_path = os.path.join(save_dir, filename)

    try:
        resp = requests.get(image_url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(resp.content)
        logger.info(f"[+] Image saved: {save_path}")
        return save_path
    except Exception as e:
        logger.error(f"[!] Image download failed: {e}")
        return None


def get_latest_football_news(limit=20):
    """Get latest football news from all sources, excluding already posted."""
    posted = load_posted()
    all_articles = []

    # Scrape all sources
    for scraper in [scrape_bbc_football, scrape_espn_football, scrape_goal_football]:
        try:
            articles = scraper()
            all_articles.extend(articles)
        except Exception as e:
            logger.error(f"[!] Scraper error: {e}")

    # Filter out already posted
    new_articles = [a for a in all_articles if a["article_id"] not in posted]

    # Deduplicate by article_id
    seen = set()
    unique = []
    for a in new_articles:
        if a["article_id"] not in seen:
            seen.add(a["article_id"])
            unique.append(a)

    logger.info(f"[+] {len(unique)} new football articles to process")
    return unique[:limit]


def get_latest_match_results():
    """Get latest match results, excluding already posted."""
    posted = load_posted()
    matches = scrape_match_results()
    new_matches = [m for m in matches if m["article_id"] not in posted]
    logger.info(f"[+] {len(new_matches)} new match results")
    return new_matches


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

    print("=== Scraping Football News ===")
    articles = get_latest_football_news(limit=5)
    for i, a in enumerate(articles):
        print(f"\n--- Article {i+1} [{a['source']}] ---")
        print(f"Title: {a['title']}")
        print(f"URL: {a['url']}")

    print("\n=== Scraping Match Results ===")
    matches = get_latest_match_results()
    for m in matches[:5]:
        print(f"{m['home_team']} {m['home_score']} - {m['away_score']} {m['away_team']}")
