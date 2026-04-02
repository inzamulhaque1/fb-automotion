"""
Sports Image Templates - ArenaHype
=====================================
Two templates:
1. News Template - Same Canva style as দেশের খবর but ArenaHype green/dark branding
2. Match Result Template - Full image bg, score pill with team logos, green bar
"""

import os
import base64
import logging
from datetime import datetime, timezone, timedelta
from html2image import Html2Image
from PIL import Image

from sports.logo_fetcher import get_logo_path

logger = logging.getLogger("SportsImageMaker")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "sports")
TEMP_DIR = os.path.join(OUTPUT_DIR, "temp")


def crop_watermark(image_path):
    if not image_path or not os.path.exists(image_path):
        return image_path
    try:
        img = Image.open(image_path)
        w, h = img.size
        img = img.crop((0, 0, w, int(h * 0.82)))
        cropped_path = image_path.rsplit(".", 1)[0] + "_cropped.jpg"
        img.save(cropped_path, "JPEG", quality=95)
        return cropped_path
    except Exception as e:
        logger.error(f"[!] Crop failed: {e}")
        return image_path


def image_to_base64(image_path):
    if not image_path or not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    ext = image_path.rsplit(".", 1)[-1].lower()
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(ext, "jpeg")
    return f"data:image/{mime};base64,{data}"


# ============================================================
# TEMPLATE 1: News Template (ArenaHype Branding)
# ============================================================

def build_news_html(title, news_image_path=None, summary="", source=""):
    """Build HTML for football news template - green/dark ArenaHype branding."""
    if news_image_path:
        news_image_path = crop_watermark(news_image_path)

    img_src = image_to_base64(news_image_path)
    img_tag = f'<img src="{img_src}" class="news-img" />' if img_src else '<div class="news-img placeholder"></div>'

    summary_line = ""
    if summary and len(summary) > 10:
        summary_line = summary[:140]
        if len(summary) > 140:
            last_space = summary_line.rfind(" ")
            if last_space > 60:
                summary_line = summary_line[:last_space]
            summary_line += "..."

    summary_html = f'<div class="content-text">{summary_line}</div>' if summary_line else ""
    source_html = ""  # No source credit on template

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Oswald:wght@400;500;600;700&display=swap');

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  html, body {{
    width: 1080px;
    height: 1080px;
    overflow: hidden;
    margin: 0;
    font-family: 'Inter', 'Segoe UI', sans-serif;
  }}

  .container {{
    width: 1080px;
    height: 1080px;
    display: flex;
    flex-direction: column;
  }}

  /* ========== TOP: IMAGE (50%) ========== */
  .image-section {{
    width: 100%;
    height: 500px;
    flex-shrink: 0;
    position: relative;
    overflow: hidden;
  }}

  .news-img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    display: block;
  }}

  .news-img.placeholder {{
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    width: 100%;
    height: 100%;
  }}

  /* ========== BRANDING BADGE ========== */
  .brand-wrapper {{
    width: 100%;
    display: flex;
    justify-content: center;
    flex-shrink: 0;
    margin-top: -24px;
    margin-bottom: -24px;
    position: relative;
    z-index: 15;
  }}

  .brand-badge {{
    background: linear-gradient(135deg, #00C853, #00E676);
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 22px 8px 12px;
    box-shadow: 0 4px 15px rgba(0,200,83,0.4);
  }}

  .fb-circle {{
    width: 36px;
    height: 36px;
    background: #1877F2;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: Arial, sans-serif;
    font-size: 22px;
    font-weight: 900;
    color: #fff;
  }}

  .page-name {{
    color: #fff;
    font-size: 20px;
    font-weight: 800;
    white-space: nowrap;
    font-family: 'Oswald', 'Inter', sans-serif;
    text-transform: uppercase;
    letter-spacing: 1px;
    text-shadow: 0 1px 3px rgba(0,0,0,0.3);
  }}

  /* ========== GREEN LINE ========== */
  .accent-line {{
    width: 100%;
    height: 5px;
    background: linear-gradient(90deg, #00C853, #00E676, #69F0AE);
    flex-shrink: 0;
    margin-top: -1px;
  }}

  /* ========== TEXT SECTION ========== */
  .text-section {{
    flex: 1;
    background: linear-gradient(180deg, #0a0a0a 0%, #111111 100%);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 25px 70px;
    text-align: center;
  }}

  .title {{
    font-family: 'Oswald', 'Inter', sans-serif;
    font-size: 48px;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.3;
    margin-bottom: 16px;
    width: 100%;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-transform: uppercase;
  }}

  .content-text {{
    font-size: 26px;
    font-weight: 400;
    color: rgba(255,255,255,0.65);
    line-height: 1.45;
    width: 100%;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }}

  .source-tag {{
    font-size: 18px;
    color: rgba(255,255,255,0.35);
    margin-top: 10px;
  }}

  /* ========== BOTTOM BAR ========== */
  .bottom-bar {{
    width: 100%;
    height: 68px;
    background: linear-gradient(90deg, #00C853, #00B848);
    display: flex;
    align-items: center;
    padding: 0 26px;
    gap: 10px;
    flex-shrink: 0;
  }}

  .action-pill {{
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(0,0,0,0.25);
    border-radius: 8px;
    padding: 8px 16px;
  }}

  .icon-box {{
    background: #fff;
    border-radius: 5px;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
  }}

  .action-label {{
    color: #fff;
    font-size: 19px;
    font-weight: 700;
    font-family: 'Inter', sans-serif;
  }}

  .readmore-btn {{
    background: #fff;
    color: #00C853;
    font-size: 19px;
    font-weight: 800;
    font-family: 'Inter', sans-serif;
    padding: 8px 22px;
    border-radius: 8px;
    margin-left: auto;
  }}
</style>
</head>
<body>
<div class="container">
  <div class="image-section">
    {img_tag}
  </div>

  <div class="brand-wrapper">
    <div class="brand-badge">
      <div class="fb-circle">f</div>
      <div class="page-name">@ArenaHype</div>
    </div>
  </div>

  <div class="accent-line"></div>

  <div class="text-section">
    <div class="title">{title}</div>
    {summary_html}
    {source_html}
  </div>

  <div class="bottom-bar">
    <div class="action-pill">
      <div class="icon-box">👍</div>
      <span class="action-label">LIKE</span>
    </div>
    <div class="action-pill">
      <div class="icon-box">💬</div>
      <span class="action-label">COMMENT</span>
    </div>
    <div class="action-pill">
      <div class="icon-box">↗</div>
      <span class="action-label">SHARE</span>
    </div>
    <div class="readmore-btn">READ MORE</div>
  </div>
</div>
</body>
</html>"""
    return html


# ============================================================
# TEMPLATE 2: Match Result Scoreboard
# ============================================================

def get_team_abbr(team_name):
    """Get 3-letter abbreviation for a team name."""
    # Common abbreviations
    abbrs = {
        # La Liga
        "real madrid": "RM", "barcelona": "FCB", "atletico madrid": "ATM",
        "real sociedad": "RSO", "villarreal": "VIL", "sevilla": "SEV",
        "real betis": "BET", "athletic bilbao": "ATH", "girona": "GIR",
        "celta vigo": "CEL", "getafe": "GET", "osasuna": "OSA",
        "mallorca": "MLL", "las palmas": "LPA", "alaves": "ALA",
        "valencia": "VAL", "cadiz": "CAD", "almeria": "ALM",
        # Premier League
        "manchester united": "MUN", "manchester city": "MCI", "liverpool": "LIV",
        "chelsea": "CHE", "arsenal": "ARS", "tottenham": "TOT", "tottenham hotspur": "TOT",
        "newcastle": "NEW", "newcastle united": "NEW", "west ham": "WHU",
        "west ham united": "WHU", "aston villa": "AVL", "everton": "EVE",
        "leicester": "LEI", "leicester city": "LEI",
        "wolves": "WOL", "wolverhampton": "WOL", "wolverhampton wanderers": "WOL",
        "brighton": "BHA", "brighton and hove albion": "BHA",
        "crystal palace": "CRY", "fulham": "FUL", "bournemouth": "BOU",
        "nottingham forest": "NFO", "brentford": "BRE", "ipswich": "IPS",
        "ipswich town": "IPS", "southampton": "SOU",
        # Bundesliga
        "bayern munich": "FCB", "bayern": "FCB", "borussia dortmund": "BVB",
        "dortmund": "BVB", "rb leipzig": "RBL", "leverkusen": "LEV",
        "bayer leverkusen": "LEV", "stuttgart": "VFB", "eintracht frankfurt": "SGE",
        "wolfsburg": "WOB", "freiburg": "SCF", "hoffenheim": "TSG",
        "union berlin": "FCU", "werder bremen": "SVW", "augsburg": "FCA",
        "mainz": "M05", "monchengladbach": "BMG", "borussia monchengladbach": "BMG",
        # Serie A
        "juventus": "JUV", "ac milan": "MIL", "inter milan": "INT", "inter": "INT",
        "napoli": "NAP", "roma": "ROM", "as roma": "ROM",
        "lazio": "LAZ", "fiorentina": "FIO", "atalanta": "ATA",
        "torino": "TOR", "bologna": "BOL", "udinese": "UDI",
        "sassuolo": "SAS", "cagliari": "CAG", "genoa": "GEN",
        "monza": "MON", "lecce": "LEC", "empoli": "EMP", "verona": "VER",
        # Ligue 1
        "paris saint-germain": "PSG", "psg": "PSG",
        "lyon": "OL", "marseille": "OM", "monaco": "MON", "lille": "LIL",
        "nice": "OGC", "rennes": "REN", "lens": "RCL", "strasbourg": "RCS",
        # Portuguese
        "benfica": "SLB", "porto": "FCP", "sporting": "SCP", "sporting cp": "SCP",
        "braga": "SCB",
        # Dutch
        "ajax": "AJX", "psv": "PSV", "feyenoord": "FEY",
        # National Teams
        "brazil": "BRA", "argentina": "ARG", "germany": "GER", "france": "FRA",
        "spain": "ESP", "england": "ENG", "portugal": "POR", "italy": "ITA",
        "netherlands": "NED", "belgium": "BEL", "uruguay": "URU", "colombia": "COL",
        "mexico": "MEX", "usa": "USA", "united states": "USA", "japan": "JPN",
        "south korea": "KOR", "australia": "AUS", "croatia": "CRO",
        "morocco": "MAR", "senegal": "SEN", "cameroon": "CMR", "nigeria": "NGA",
        "ghana": "GHA", "egypt": "EGY", "saudi arabia": "KSA", "qatar": "QAT",
        "iran": "IRN", "turkey": "TUR", "poland": "POL", "switzerland": "SUI",
        "denmark": "DEN", "sweden": "SWE", "norway": "NOR", "austria": "AUT",
        "czech republic": "CZE", "serbia": "SRB", "scotland": "SCO",
        "wales": "WAL", "ireland": "IRL", "bangladesh": "BAN",
        # Saudi Pro League
        "al nassr": "NAS", "al hilal": "HIL", "al ahli": "AHL", "al ittihad": "ITT",
        "al shabab": "SHB", "al fateh": "FAT", "al taawoun": "TAA", "al ettifaq": "ETF",
        # MLS
        "inter miami": "MIA", "inter miami cf": "MIA", "la galaxy": "LAG",
        "lafc": "LAFC", "los angeles fc": "LAFC", "new york red bulls": "NYRB",
        "new york city fc": "NYC", "atlanta united": "ATL",
        "seattle sounders": "SEA", "portland timbers": "POR",
        "columbus crew": "CLB", "fc cincinnati": "CIN", "nashville sc": "NSH",
        "austin fc": "ATX", "toronto fc": "TFC", "cf montreal": "MTL",
        "orlando city": "ORL", "dc united": "DCU", "houston dynamo": "HOU",
        "philadelphia union": "PHI",
        # Copa Libertadores
        "flamengo": "FLA", "palmeiras": "PAL", "river plate": "RIV",
        "boca juniors": "BOC", "gremio": "GRE", "corinthians": "COR",
        "sao paulo": "SAO", "santos": "SAN", "atletico mineiro": "CAM",
        "fluminense": "FLU", "internacional": "INT", "cruzeiro": "CRU",
        "penarol": "PEN", "nacional": "NAC", "independiente": "IND",
        "racing club": "RAC", "cerro porteno": "CER", "olimpia": "OLI",
    }
    key = team_name.lower().strip()
    if key in abbrs:
        return abbrs[key]
    # Fallback: first 3 letters uppercase
    words = team_name.split()
    if len(words) >= 3:
        return "".join(w[0] for w in words[:3]).upper()
    return team_name[:3].upper()


def get_team_color(team_name):
    """Get primary color for a team."""
    colors = {
        "real madrid": "#FFFFFF", "barcelona": "#A50044", "atletico madrid": "#CB3524",
        "manchester united": "#DA291C", "manchester city": "#6CABDD", "liverpool": "#C8102E",
        "chelsea": "#034694", "arsenal": "#EF0107", "tottenham": "#132257",
        "bayern munich": "#DC052D", "bayern": "#DC052D", "borussia dortmund": "#FDE100",
        "dortmund": "#FDE100", "paris saint-germain": "#004170", "psg": "#004170",
        "juventus": "#000000", "ac milan": "#FB090B", "inter milan": "#009FE3", "inter": "#009FE3",
        "napoli": "#12A0D7", "roma": "#8E1F2F", "lazio": "#87D8F7",
        "benfica": "#E20613", "porto": "#003893", "ajax": "#D2122E",
        "brazil": "#009739", "argentina": "#75AADB", "germany": "#000000",
        "france": "#002654", "spain": "#AA151B", "england": "#FFFFFF",
        "portugal": "#006600", "italy": "#0066B2", "netherlands": "#FF6600",
        "belgium": "#ED2939", "newcastle": "#241F20", "west ham": "#7A263A",
        "aston villa": "#670E36", "everton": "#003399", "leicester": "#003090",
        "wolves": "#FDB913", "brighton": "#0057B8", "crystal palace": "#1B458F",
        "rb leipzig": "#DD0741", "leverkusen": "#E32221", "bayer leverkusen": "#E32221",
        "lyon": "#0B3C8E", "marseille": "#2FAEE0", "monaco": "#E7152A",
        "fiorentina": "#482B8C", "atalanta": "#1E71B8",
        # Saudi Pro League
        "al nassr": "#FEDF00", "al hilal": "#1A3C7E", "al ahli": "#006633",
        "al ittihad": "#FFD700", "al ettifaq": "#006838",
        # MLS
        "inter miami": "#F7B5CD", "la galaxy": "#00245D", "lafc": "#C39E6D",
        "los angeles fc": "#C39E6D", "atlanta united": "#80000A",
        "seattle sounders": "#658D1B", "new york red bulls": "#ED1E36",
        "new york city fc": "#6CACE4", "orlando city": "#633492",
        "toronto fc": "#E31937", "columbus crew": "#FEDD00",
        # Copa Libertadores
        "flamengo": "#C72C30", "palmeiras": "#006437", "river plate": "#E4002B",
        "boca juniors": "#003DA5", "gremio": "#0065A4", "corinthians": "#000000",
        "sao paulo": "#FF0000", "fluminense": "#7B2D4B", "santos": "#000000",
    }
    key = team_name.lower().strip()
    return colors.get(key, "#1a5c3a")


def build_match_result_html(home_team, away_team, home_score, away_score, competition="", status="Full Time", home_logo_b64="", away_logo_b64=""):
    """Build HTML for match result - reference style: full image bg, score pill with logos, green bar."""

    home_abbr = get_team_abbr(home_team)
    away_abbr = get_team_abbr(away_team)
    home_color = get_team_color(home_team)
    away_color = get_team_color(away_team)

    # Home team logo/crest
    if home_logo_b64:
        home_crest = f'<img src="{home_logo_b64}" class="logo-img" />'
    else:
        home_crest = f'<div class="logo-fallback" style="background:{home_color};">{home_abbr}</div>'

    # Away team logo/crest
    if away_logo_b64:
        away_crest = f'<img src="{away_logo_b64}" class="logo-img" />'
    else:
        away_crest = f'<div class="logo-fallback" style="background:{away_color};">{away_abbr}</div>'

    competition_html = f'<div class="comp-name">{competition}</div>' if competition else ""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Oswald:wght@400;500;600;700&display=swap');

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  html, body {{
    width: 1080px;
    height: 1080px;
    overflow: hidden;
    margin: 0;
    font-family: 'Inter', sans-serif;
  }}

  .container {{
    width: 1080px;
    height: 1080px;
    display: flex;
    flex-direction: column;
    position: relative;
  }}

  /* ========== TOP IMAGE SECTION (~75%) ========== */
  .image-section {{
    width: 100%;
    height: 740px;
    flex-shrink: 0;
    position: relative;
    overflow: hidden;
    /* Stadium background with CSS */
    background:
      /* Floodlights top */
      radial-gradient(ellipse at 25% 8%, rgba(255,255,255,0.5) 0%, rgba(200,230,255,0.15) 15%, transparent 40%),
      radial-gradient(ellipse at 75% 8%, rgba(255,255,255,0.5) 0%, rgba(200,230,255,0.15) 15%, transparent 40%),
      radial-gradient(ellipse at 50% 5%, rgba(200,220,255,0.3) 0%, transparent 35%),
      /* Stadium crowd */
      radial-gradient(ellipse at 50% 45%, rgba(30,60,100,0.6) 0%, transparent 70%),
      /* Sky */
      linear-gradient(180deg,
        #0a1628 0%,
        #0f2540 15%,
        #153050 30%,
        #1a3d5e 45%,
        #1a4a3a 70%,
        #0d3520 85%,
        #0a2a18 100%
      );
  }}

  /* Grass field at bottom of image */
  .image-section::after {{
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 250px;
    background:
      linear-gradient(180deg,
        transparent 0%,
        rgba(15,80,30,0.4) 20%,
        rgba(20,100,35,0.6) 40%,
        rgba(25,120,40,0.7) 60%,
        rgba(30,90,30,0.8) 80%,
        rgba(20,70,25,0.9) 100%
      );
  }}

  /* Stadium crowd texture */
  .image-section::before {{
    content: '';
    position: absolute;
    top: 25%; left: 0; right: 0;
    height: 45%;
    background:
      repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(100,150,200,0.03) 2px, rgba(100,150,200,0.03) 4px),
      repeating-linear-gradient(90deg, transparent, transparent 8px, rgba(80,130,180,0.02) 8px, rgba(80,130,180,0.02) 16px);
    z-index: 1;
  }}

  /* ========== BRANDING BADGE (overlapping center) ========== */
  .brand-wrapper {{
    width: 100%;
    display: flex;
    justify-content: center;
    flex-shrink: 0;
    margin-top: -26px;
    margin-bottom: -26px;
    position: relative;
    z-index: 15;
  }}

  .brand-badge {{
    background: linear-gradient(135deg, #00C853, #00E676);
    border-radius: 10px;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 26px 10px 14px;
    box-shadow: 0 4px 20px rgba(0,200,83,0.5);
  }}

  .fb-circle {{
    width: 40px;
    height: 40px;
    background: #1877F2;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: Arial, sans-serif;
    font-size: 24px;
    font-weight: 900;
    color: #fff;
  }}

  .page-name {{
    color: #fff;
    font-family: 'Oswald', sans-serif;
    font-size: 22px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    text-shadow: 0 1px 3px rgba(0,0,0,0.3);
  }}

  /* ========== SCORE SECTION (black bg) ========== */
  .score-section {{
    flex: 1;
    background: #000;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 30px 40px 15px;
  }}

  {competition_html and '''
  .comp-name {
    font-family: "Oswald", sans-serif;
    font-size: 20px;
    font-weight: 500;
    color: rgba(255,255,255,0.4);
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-bottom: 5px;
  }
  ''' or ''}

  /* ========== SCORE PILL ========== */
  .score-pill {{
    display: flex;
    align-items: center;
    gap: 0;
    background: linear-gradient(135deg, #FFD600, #FFAB00);
    border-radius: 60px;
    padding: 8px 10px;
    box-shadow: 0 6px 25px rgba(255,214,0,0.35);
  }}

  .team-logo {{
    width: 90px;
    height: 90px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    background: transparent;
  }}

  .logo-img {{
    width: 85px;
    height: 85px;
    object-fit: contain;
  }}

  .logo-fallback {{
    width: 100%;
    height: 100%;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Oswald', sans-serif;
    font-size: 30px;
    font-weight: 900;
    color: #fff;
    letter-spacing: 1px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
  }}

  .score-text {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0 20px;
  }}

  .score-num {{
    font-family: 'Oswald', sans-serif;
    font-size: 72px;
    font-weight: 900;
    color: #000;
    line-height: 1;
  }}

  .score-dash {{
    font-family: 'Oswald', sans-serif;
    font-size: 50px;
    font-weight: 600;
    color: rgba(0,0,0,0.5);
    line-height: 1;
  }}

  /* ========== BOTTOM GREEN BAR ========== */
  .bottom-bar {{
    width: 100%;
    height: 74px;
    background: linear-gradient(90deg, #00C853, #00B848);
    display: flex;
    align-items: center;
    padding: 0 28px;
    gap: 12px;
    flex-shrink: 0;
  }}

  .action-pill {{
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(0,0,0,0.25);
    border-radius: 8px;
    padding: 10px 18px;
  }}

  .icon-box {{
    background: #fff;
    border-radius: 5px;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
  }}

  .action-label {{
    color: #fff;
    font-size: 20px;
    font-weight: 700;
    font-family: 'Inter', sans-serif;
  }}

  .readmore-btn {{
    background: #fff;
    color: #00C853;
    font-size: 20px;
    font-weight: 800;
    font-family: 'Inter', sans-serif;
    font-style: italic;
    padding: 10px 24px;
    border-radius: 8px;
    margin-left: auto;
  }}
</style>
</head>
<body>
<div class="container">
  <!-- TOP: Stadium Image -->
  <div class="image-section"></div>

  <!-- CENTER: Branding Badge (overlapping) -->
  <div class="brand-wrapper">
    <div class="brand-badge">
      <div class="fb-circle">f</div>
      <div class="page-name">@ArenaHype</div>
    </div>
  </div>

  <!-- SCORE SECTION -->
  <div class="score-section">
    {competition_html}

    <div class="score-pill">
      <div class="team-logo">{home_crest}</div>
      <div class="score-text">
        <div class="score-num">{home_score}</div>
        <div class="score-dash">-</div>
        <div class="score-num">{away_score}</div>
      </div>
      <div class="team-logo">{away_crest}</div>
    </div>
  </div>

  <!-- BOTTOM: Green Bar -->
  <div class="bottom-bar">
    <div class="action-pill">
      <div class="icon-box">👍</div>
      <span class="action-label">LIKE</span>
    </div>
    <div class="action-pill">
      <div class="icon-box">💬</div>
      <span class="action-label">COMMENT</span>
    </div>
    <div class="action-pill">
      <div class="icon-box">↗</div>
      <span class="action-label">SHARE</span>
    </div>
    <div class="readmore-btn">READ MORE</div>
  </div>
</div>
</body>
</html>"""
    return html


# ============================================================
# Image Generation Functions
# ============================================================

def _render_html(html, filename):
    """Render HTML to image using html2image."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

    try:
        hti = Html2Image(
            output_path=OUTPUT_DIR,
            size=(1080, 1200),
            custom_flags=[
                "--no-sandbox",
                "--disable-gpu",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                "--window-size=1080,1200",
            ],
        )
        paths = hti.screenshot(html_str=html, save_as=filename)
        raw_path = paths[0] if paths else os.path.join(OUTPUT_DIR, filename)

        # Crop to exact 1080x1080
        img = Image.open(raw_path)
        if img.size != (1080, 1080):
            img = img.crop((0, 0, 1080, 1080))
            img.save(raw_path)

        logger.info(f"[+] Image created: {raw_path}")
        return raw_path
    except Exception as e:
        logger.error(f"[!] Image creation failed: {e}")
        return None


def create_news_image(title, news_image_path=None, article_id="", summary="", source=""):
    """Create a football news template image."""
    now = datetime.now(timezone.utc)
    filename = f"sports_{article_id}_{now.strftime('%Y%m%d_%H%M%S')}.png"
    html = build_news_html(title, news_image_path, summary, source)
    return _render_html(html, filename)


def create_match_result_image(home_team, away_team, home_score, away_score, competition="", status="Full Time", match_id=""):
    """Create a match result image with team logos."""
    now = datetime.now(timezone.utc)
    filename = f"match_{match_id}_{now.strftime('%Y%m%d_%H%M%S')}.png"

    # Try to load team logos
    home_logo_b64 = ""
    away_logo_b64 = ""

    home_logo_path = get_logo_path(home_team)
    if home_logo_path:
        home_logo_b64 = image_to_base64(home_logo_path)

    away_logo_path = get_logo_path(away_team)
    if away_logo_path:
        away_logo_b64 = image_to_base64(away_logo_path)

    html = build_match_result_html(
        home_team, away_team, home_score, away_score,
        competition, status, home_logo_b64, away_logo_b64,
    )
    return _render_html(html, filename)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

    print("=== Test News Template ===")
    path1 = create_news_image(
        title="Mbappe Scores Hat-trick as Real Madrid Thrash Barcelona 5-2 in El Clasico",
        summary="Kylian Mbappe was on fire as Real Madrid demolished Barcelona in an unforgettable El Clasico clash.",
        source="BBC Sport",
        article_id="test_news",
    )
    print(f"News image: {path1}")

    print("\n=== Test Match Result Template ===")
    path2 = create_match_result_image(
        home_team="Real Madrid",
        away_team="Barcelona",
        home_score="5",
        away_score="2",
        competition="La Liga",
        match_id="test_match",
    )
    print(f"Match result image: {path2}")
