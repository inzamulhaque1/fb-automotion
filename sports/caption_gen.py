"""
Football Caption Generator - ArenaHype
========================================
Generates engaging English captions for football news & match results using Groq API.
"""

import os
import logging
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("SportsCaptionGen")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


def generate_news_caption(title, summary="", source=""):
    """Generate an engaging English caption for a football news post."""
    if not GROQ_API_KEY:
        logger.error("[!] GROQ_API_KEY not set")
        return fallback_news_caption(title)

    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""You are the social media manager for "ArenaHype" — a viral football news page on Facebook. Write an engaging caption for this football news post.

News headline: {title}
{f'Summary: {summary}' if summary else ''}
{f'Source: {source}' if source else ''}

Caption format:
1. Start with ⚽ and a bold hook line (rewrite the headline to be more engaging, 1 line)
2. Leave a blank line
3. 2-3 lines of key info from the article (informative, concise)
4. Leave a blank line
5. "👉 Follow ArenaHype for daily football updates, transfer news & match results!"
6. Leave a blank line
7. 4-5 relevant hashtags (mix of general and specific, e.g. #Football #PremierLeague #TransferNews)

Rules:
- Write in English only
- No links
- Professional but exciting tone, like a football fan who knows the game
- Keep it under 200 words
- Just write the caption, nothing else:"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300,
        )
        caption = response.choices[0].message.content.strip()
        logger.info(f"[+] News caption generated: {caption[:80]}...")
        return caption
    except Exception as e:
        logger.error(f"[!] Groq API error: {e}")
        return fallback_news_caption(title)


def generate_match_caption(home_team, away_team, home_score, away_score, competition=""):
    """Generate an engaging caption for a match result post."""
    if not GROQ_API_KEY:
        logger.error("[!] GROQ_API_KEY not set")
        return fallback_match_caption(home_team, away_team, home_score, away_score)

    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""You are the social media manager for "ArenaHype" — a viral football page on Facebook. Write an engaging caption for this match result.

Match: {home_team} {home_score} - {away_score} {away_team}
{f'Competition: {competition}' if competition else ''}

Caption format:
1. Start with 🏆 or ⚽ and a dramatic one-liner about the result (who won/drew, was it an upset?)
2. Leave a blank line
3. The scoreline in a clean format: "{home_team} {home_score} - {away_score} {away_team}"
4. Leave a blank line
5. 2-3 lines of quick analysis/reaction (what this means for the table, key moments, etc.)
6. Leave a blank line
7. "👉 Follow ArenaHype for live scores, highlights & football news!"
8. Leave a blank line
9. 4-5 hashtags

Rules:
- English only, no links
- Exciting football commentator tone
- Under 150 words
- Just write the caption:"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=250,
        )
        caption = response.choices[0].message.content.strip()
        logger.info(f"[+] Match caption generated: {caption[:80]}...")
        return caption
    except Exception as e:
        logger.error(f"[!] Groq API error: {e}")
        return fallback_match_caption(home_team, away_team, home_score, away_score)


def fallback_news_caption(title):
    return (
        f"⚽ {title}\n\n"
        f"Stay updated with the latest football news!\n\n"
        f"👉 Follow ArenaHype for daily football updates!\n\n"
        f"#Football #Soccer #ArenaHype #FootballNews"
    )


def fallback_match_caption(home_team, away_team, home_score, away_score):
    return (
        f"⚽ Full Time!\n\n"
        f"{home_team} {home_score} - {away_score} {away_team}\n\n"
        f"What a match! Drop your thoughts below 👇\n\n"
        f"👉 Follow ArenaHype for live scores & highlights!\n\n"
        f"#Football #MatchDay #ArenaHype #FullTime"
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=== Test News Caption ===")
    caption = generate_news_caption(
        "Mbappe scores hat-trick as Real Madrid thrash Barcelona 5-2",
        "Kylian Mbappe was on fire as Real Madrid demolished Barcelona in an El Clasico to remember."
    )
    print(caption)

    print("\n=== Test Match Caption ===")
    caption = generate_match_caption("Real Madrid", "Barcelona", "5", "2", "La Liga")
    print(caption)
