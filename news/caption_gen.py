"""
AI Caption Generator - Groq
=============================
Generates engaging Bangla captions for news posts using Groq API.
"""

import os
import logging
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("CaptionGen")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


def generate_caption(title, summary="", category="national"):
    """
    Generate an engaging Bangla caption for a news post.

    Args:
        title: News article title (Bangla)
        summary: Article summary text
        category: News category

    Returns:
        str: Generated caption for FB post
    """
    if not GROQ_API_KEY:
        logger.error("[!] GROQ_API_KEY not set")
        return fallback_caption(title)

    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""তুমি "দেশের খবর - Desher Khobor" ফেসবুক নিউজ পেজের এক্সপার্ট কপিরাইটার। নিচের খবরটির জন্য একটি ভাইরাল-স্টাইল ফেসবুক ক্যাপশন লেখো।

নিউজ শিরোনাম: {title}
{f'সারসংক্ষেপ: {summary}' if summary else ''}
ক্যাটাগরি: {category}

ক্যাপশনের ফরম্যাট:
1. প্রথম লাইনে 🔴 দিয়ে শুরু করো এবং একটি আকর্ষণীয় হুক লেখো (শিরোনামের সারমর্ম, ১ লাইন)
2. তারপর ১ লাইন ফাঁকা রাখো
3. ২-৩ লাইনে খবরের মূল তথ্য দাও (তথ্যবহুল, সংক্ষেপে)
4. তারপর ১ লাইন ফাঁকা রাখো
5. "👉 এই ধরনের গুরুত্বপূর্ণ খবর সবার আগে পেতে আমাদের পেজ 'দেশের খবর - Desher Khobor' ফলো করুন!"
6. তারপর ১ লাইন ফাঁকা রাখো
7. ৪-৫টি প্রাসঙ্গিক হ্যাশট্যাগ (বাংলা + English mix, যেমন #বাংলাদেশ #BreakingNews)

নিয়ম:
- সম্পূর্ণ বাংলায় লেখো (হ্যাশট্যাগ ছাড়া)
- কোনো লিংক দিও না
- প্রফেশনাল কিন্তু engaging টোন রাখো
- শুধু ক্যাপশনটি লেখো:"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300,
        )
        caption = response.choices[0].message.content.strip()
        logger.info(f"[+] Caption generated: {caption[:80]}...")
        return caption
    except Exception as e:
        logger.error(f"[!] Groq API error: {e}")
        return fallback_caption(title)


def fallback_caption(title):
    """Simple fallback caption if AI fails."""
    return (
        f"📰 {title}\n\n"
        f"বিস্তারিত জানতে পোস্টটি পড়ুন।\n\n"
        f"দেশের খবর ফলো করুন সবার আগে খবর পেতে।\n\n"
        f"#দেশেরখবর #বাংলাদেশ #DesherKhobor"
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_title = "২২ জেলায় বইছে তাপপ্রবাহ"
    test_summary = "দেশের ২২ জেলায় মৃদু থেকে তীব্র তাপপ্রবাহ বয়ে যাচ্ছে।"
    caption = generate_caption(test_title, test_summary)
    print("\n=== Generated Caption ===")
    print(caption)
