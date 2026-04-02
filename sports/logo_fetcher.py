"""
Team Logo Fetcher - ArenaHype
==============================
Downloads and caches team logos from public sources.
- Country flags from flagcdn.com
- Club logos from ESPN CDN
"""

import os
import logging
import requests

logger = logging.getLogger("LogoFetcher")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_DIR = os.path.join(BASE_DIR, "assets", "logos")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

# Country code mapping (team name -> ISO 2-letter code for flagcdn.com)
COUNTRY_CODES = {
    "brazil": "br", "argentina": "ar", "germany": "de", "france": "fr",
    "spain": "es", "england": "gb-eng", "portugal": "pt", "italy": "it",
    "netherlands": "nl", "belgium": "be", "uruguay": "uy", "colombia": "co",
    "mexico": "mx", "usa": "us", "united states": "us", "japan": "jp",
    "south korea": "kr", "australia": "au", "croatia": "hr", "morocco": "ma",
    "senegal": "sn", "cameroon": "cm", "nigeria": "ng", "ghana": "gh",
    "egypt": "eg", "saudi arabia": "sa", "qatar": "qa", "iran": "ir",
    "turkey": "tr", "poland": "pl", "switzerland": "ch", "denmark": "dk",
    "sweden": "se", "norway": "no", "austria": "at", "czech republic": "cz",
    "serbia": "rs", "scotland": "gb-sct", "wales": "gb-wls",
    "ireland": "ie", "bangladesh": "bd", "canada": "ca", "chile": "cl",
    "peru": "pe", "ecuador": "ec", "paraguay": "py", "bolivia": "bo",
    "venezuela": "ve", "costa rica": "cr", "panama": "pa", "honduras": "hn",
    "jamaica": "jm", "tunisia": "tn", "algeria": "dz", "south africa": "za",
    "ivory coast": "ci", "congo": "cd", "mali": "ml", "burkina faso": "bf",
    "india": "in", "china": "cn", "indonesia": "id", "thailand": "th",
    "vietnam": "vn", "philippines": "ph", "malaysia": "my",
    "ukraine": "ua", "romania": "ro", "greece": "gr", "hungary": "hu",
    "slovakia": "sk", "slovenia": "si", "bosnia": "ba",
    "bosnia and herzegovina": "ba", "albania": "al", "north macedonia": "mk",
    "montenegro": "me", "iceland": "is", "finland": "fi",
    "russia": "ru", "georgia": "ge",
}

# ESPN team ID mapping (team name -> ESPN soccer team ID)
ESPN_TEAM_IDS = {
    # La Liga
    "real madrid": 86, "barcelona": 83, "atletico madrid": 1068,
    "sevilla": 243, "villarreal": 102, "real sociedad": 89,
    "real betis": 244, "athletic bilbao": 93, "valencia": 94,
    "girona": 9812, "celta vigo": 3842, "getafe": 3751,
    "osasuna": 97, "mallorca": 3023, "las palmas": 3022,
    # Premier League
    "manchester united": 360, "manchester city": 382, "liverpool": 364,
    "chelsea": 363, "arsenal": 359, "tottenham": 367, "tottenham hotspur": 367,
    "newcastle": 361, "newcastle united": 361, "west ham": 371,
    "west ham united": 371, "aston villa": 362, "everton": 368,
    "leicester": 375, "leicester city": 375,
    "wolves": 380, "wolverhampton": 380, "brighton": 331,
    "crystal palace": 384, "fulham": 370, "bournemouth": 349,
    "nottingham forest": 393, "brentford": 337, "ipswich": 373,
    "southampton": 376,
    # Bundesliga
    "bayern munich": 132, "bayern": 132, "borussia dortmund": 124, "dortmund": 124,
    "rb leipzig": 11420, "leverkusen": 131, "bayer leverkusen": 131,
    "eintracht frankfurt": 125, "wolfsburg": 134, "freiburg": 5765,
    "hoffenheim": 5765, "stuttgart": 130, "union berlin": 11358,
    "werder bremen": 133, "augsburg": 9789, "mainz": 8714,
    "monchengladbach": 126, "borussia monchengladbach": 126,
    # Serie A
    "juventus": 111, "ac milan": 103, "inter milan": 110, "inter": 110,
    "napoli": 114, "roma": 104, "as roma": 104, "lazio": 105,
    "fiorentina": 109, "atalanta": 107, "torino": 113, "bologna": 108,
    "udinese": 115, "genoa": 3753, "monza": 18414, "cagliari": 3189,
    "lecce": 3188, "empoli": 3520, "verona": 3119,
    # Ligue 1
    "paris saint-germain": 160, "psg": 160, "lyon": 167, "marseille": 176,
    "monaco": 174, "lille": 166, "nice": 172, "rennes": 177, "lens": 170,
    # Portuguese
    "benfica": 1903, "porto": 437, "sporting": 439, "sporting cp": 439,
    # Dutch
    "ajax": 139, "psv": 148, "feyenoord": 143,
    # Saudi Pro League
    "al nassr": 23585, "al hilal": 5765, "al ahli": 23598, "al ittihad": 2667,
    # MLS
    "inter miami": 22492, "la galaxy": 184, "lafc": 21261,
    "atlanta united": 18296, "seattle sounders": 9726, "new york red bulls": 190,
    "new york city fc": 17012, "orlando city": 14205, "toronto fc": 9723,
    "columbus crew": 183, "fc cincinnati": 19079, "nashville sc": 21192,
    # Copa Libertadores
    "flamengo": 819, "palmeiras": 2036, "river plate": 793, "boca juniors": 792,
    "gremio": 802, "corinthians": 826, "sao paulo": 830, "santos": 831,
    "atletico mineiro": 2175, "fluminense": 803, "internacional": 2165,
    "cruzeiro": 2154, "penarol": 6678, "nacional": 6679,
}


def get_logo_path(team_name):
    """Get the cached logo path for a team. Downloads if not cached."""
    os.makedirs(LOGO_DIR, exist_ok=True)

    key = team_name.lower().strip()
    safe_name = key.replace(" ", "_").replace(".", "")

    # Check if already cached
    for ext in ["png", "svg", "jpg"]:
        cached = os.path.join(LOGO_DIR, f"{safe_name}.{ext}")
        if os.path.exists(cached) and os.path.getsize(cached) > 100:
            return cached

    # Try to download
    logo_path = _download_logo(key, safe_name)
    return logo_path


def _download_logo(team_key, safe_name):
    """Try to download logo from available sources."""

    # 1. Try country flag first (flagcdn.com)
    if team_key in COUNTRY_CODES:
        code = COUNTRY_CODES[team_key]
        url = f"https://flagcdn.com/w320/{code}.png"
        path = os.path.join(LOGO_DIR, f"{safe_name}.png")
        if _download_file(url, path):
            return path

    # 2. Try ESPN club logo
    if team_key in ESPN_TEAM_IDS:
        team_id = ESPN_TEAM_IDS[team_key]
        url = f"https://a.espncdn.com/i/teamlogos/soccer/500/{team_id}.png"
        path = os.path.join(LOGO_DIR, f"{safe_name}.png")
        if _download_file(url, path):
            return path

    # 3. No logo found
    logger.warning(f"[!] No logo found for: {team_key}")
    return None


def _download_file(url, save_path):
    """Download a file and return True if successful."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200 and len(resp.content) > 100:
            with open(save_path, "wb") as f:
                f.write(resp.content)
            logger.info(f"[+] Logo saved: {os.path.basename(save_path)}")
            return True
    except Exception as e:
        logger.error(f"[!] Download failed {url}: {e}")
    return False


def preload_logos(team_names):
    """Pre-download logos for a list of teams."""
    results = {}
    for name in team_names:
        path = get_logo_path(name)
        results[name] = path
        if path:
            logger.info(f"[+] {name}: {os.path.basename(path)}")
        else:
            logger.warning(f"[!] {name}: no logo")
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

    test_teams = [
        "Brazil", "Croatia", "Argentina", "Real Madrid", "Barcelona",
        "Liverpool", "Manchester City", "Al Nassr", "Inter Miami",
        "Flamengo", "Boca Juniors",
    ]

    print("=== Downloading Team Logos ===")
    results = preload_logos(test_teams)
    for team, path in results.items():
        status = f"OK: {path}" if path else "MISSING"
        print(f"  {team}: {status}")
