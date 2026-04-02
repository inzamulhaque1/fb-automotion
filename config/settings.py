import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# FB Automotion - Settings
# ============================================

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "input", "raw_videos")
OUTPUT_GAMING_DIR = os.path.join(BASE_DIR, "output", "gaming")
OUTPUT_PERSONAL_DIR = os.path.join(BASE_DIR, "output", "personal")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

# --- Facebook API ---
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN", "")
FB_GAMING_PAGE_ID = os.getenv("FB_GAMING_PAGE_ID", "")
FB_PERSONAL_PAGE_ID = os.getenv("FB_PERSONAL_PAGE_ID", "")
FB_NEWS_PAGE_ID = os.getenv("FB_NEWS_PAGE_ID", "")

# --- FTP Server ---
FTP_HOST = "0.0.0.0"
FTP_PORT = 2121
FTP_USER = os.getenv("FTP_USER", "inzamul")
FTP_PASS = os.getenv("FTP_PASS", "automotion2026")
FTP_UPLOAD_DIR = INPUT_DIR

# --- Gaming Page: INZ-Gaming ---
GAMING = {
    "page_name": "INZ-Gaming",
    "daily_posts": 12,
    "video_lengths": [3, 5, 8],  # minutes
    "theme": {
        "primary": "#FF0000",     # Red
        "secondary": "#000000",   # Black
        "text_color": "#FFFFFF",  # White
        "font_size": 48,
    },
    "watermark_text": "INZ-Gaming",
    "music_volume": 0.3,
}

# --- Personal Page: Inzamul Haque ---
PERSONAL = {
    "page_name": "Inzamul Haque",
    "daily_posts": 10,
    "theme": {
        "primary": "#2196F3",     # Blue
        "secondary": "#FFFFFF",   # White
        "accent": "#1565C0",      # Dark Blue
        "text_color": "#333333",  # Dark Gray
        "font_size": 36,
    },
    "languages": ["en", "bn"],
    "content_types": ["ai_news", "web_dev_tips", "image_card", "thread"],
}

# --- News Page: Desher Khobor ---
NEWS = {
    "page_name": "দেশের খবর",
    "page_name_en": "Desher Khobor",
    "source": "https://www.jagonews24.com",
    "theme": {
        "primary": "#D32F2F",     # Red
        "secondary": "#FFFFFF",   # White
        "text_color": "#000000",  # Black
        "highlight": "#D32F2F",   # Red for names
        "font_size": 42,
    },
    "languages": ["bn"],
}

# --- AI API ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# --- Dashboard ---
DASHBOARD_HOST = "0.0.0.0"
DASHBOARD_PORT = 5000
DASHBOARD_DEBUG = True
