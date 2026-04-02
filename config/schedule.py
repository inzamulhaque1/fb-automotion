# ============================================
# Posting Schedule Configuration
# ============================================

# Gaming: 12 videos spread across the day (peak hours focused)
GAMING_SCHEDULE = {
    "posts_per_day": 12,
    "time_slots": [
        "08:00", "09:30", "11:00",   # Morning
        "12:30", "14:00", "15:30",   # Afternoon
        "17:00", "18:30", "19:30",   # Evening (peak)
        "20:30", "21:30", "22:30",   # Night (peak)
    ],
    "timezone": "Asia/Dhaka",
}

# Personal: 10 posts spread across the day
PERSONAL_SCHEDULE = {
    "posts_per_day": 10,
    "time_slots": [
        "07:00", "09:00", "10:30",   # Morning
        "12:00", "13:30", "15:00",   # Afternoon
        "17:00", "19:00",            # Evening
        "21:00", "22:00",            # Night
    ],
    "timezone": "Asia/Dhaka",
    "content_distribution": {
        "ai_news": 4,
        "web_dev_tips": 4,
        "thread": 2,
    },
}
