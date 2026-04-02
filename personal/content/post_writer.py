"""
Post Writer - Thread & engagement posts
==========================================
Long-form threads and engagement-focused content.
AI influencer style.
"""

import random
import logging

logger = logging.getLogger("PostWriter")

THREAD_POSTS = [
    {
        "title": "The AI Revolution is Here",
        "lang": "en",
        "text": (
            "I'm going to be brutally honest with you.\n\n"
            "If you're not learning AI right now, you'll regret it in 2 years.\n\n"
            "Here's what's happening that most people don't realize:\n\n"
            "- AI can now write better than 90% of humans\n"
            "- AI can code entire applications from a description\n"
            "- AI can create images, videos, music from text\n"
            "- AI can analyze data faster than any analyst\n"
            "- AI can automate 80% of repetitive tasks\n\n"
            "This isn't the future. This is RIGHT NOW.\n\n"
            "Companies are already:\n"
            "- Replacing junior roles with AI\n"
            "- Hiring 'AI-native' workers at premium salaries\n"
            "- Automating entire departments\n\n"
            "The good news?\n"
            "It's not too late. But the window is closing.\n\n"
            "Start here:\n"
            "1. Use ChatGPT or Claude daily\n"
            "2. Automate one task this week\n"
            "3. Learn prompt engineering\n"
            "4. Build something with AI\n\n"
            "The people who act now will lead the next decade.\n\n"
            "Which side will you be on?\n\n"
            "Follow Inzamul Haque for daily AI insights.\n\n"
            "#AI #FutureOfWork #Tech #Motivation"
        ),
    },
    {
        "title": "Why Most People Will Fail With AI",
        "lang": "en",
        "text": (
            "Hot take: 95% of people using AI are using it WRONG.\n\n"
            "They type 'write me a blog post' and get garbage.\n"
            "Then they say 'AI is overhyped.'\n\n"
            "Here's the truth:\n\n"
            "AI is a tool. Like a guitar.\n"
            "Hand someone a guitar - they make noise.\n"
            "Hand a musician a guitar - they make magic.\n\n"
            "The difference? SKILL.\n\n"
            "5 mistakes people make with AI:\n\n"
            "1. Vague prompts ('write something good')\n"
            "   Fix: Be specific about format, tone, audience\n\n"
            "2. Not giving context\n"
            "   Fix: Tell AI who you are and what you need\n\n"
            "3. Accepting first output\n"
            "   Fix: Iterate, refine, ask for improvements\n\n"
            "4. Using only ChatGPT\n"
            "   Fix: Try Claude, Perplexity, specialized tools\n\n"
            "5. Not automating\n"
            "   Fix: Connect AI to your workflow with APIs\n\n"
            "Master these and you'll be in the top 5%.\n\n"
            "Follow Inzamul Haque for AI mastery tips.\n\n"
            "#AI #PromptEngineering #Productivity #Tech"
        ),
    },
    {
        "title": "Build Your Personal Brand With AI",
        "lang": "en",
        "text": (
            "I built a personal brand that posts 10x/day.\n"
            "I spend 0 hours creating content.\n\n"
            "Here's my exact system (I'm sharing everything):\n\n"
            "Step 1: Content Research\n"
            "- AI scrapes trending topics in my niche\n"
            "- Filters the best ones automatically\n\n"
            "Step 2: Content Creation\n"
            "- AI writes posts in my voice and style\n"
            "- Generates images and cards\n"
            "- Creates engaging hooks\n\n"
            "Step 3: Scheduling\n"
            "- Posts go out at peak engagement times\n"
            "- Different content types throughout the day\n"
            "- Fully automated pipeline\n\n"
            "Step 4: Engagement\n"
            "- AI suggests replies to comments\n"
            "- Analytics track what works\n"
            "- System improves over time\n\n"
            "Result:\n"
            "- 10+ posts/day across platforms\n"
            "- Growing audience on autopilot\n"
            "- More time for actual work\n\n"
            "Want to build something like this?\n"
            "Comment 'SYSTEM' and I'll share more details.\n\n"
            "Follow Inzamul Haque\n\n"
            "#PersonalBrand #AI #Automation #ContentCreation"
        ),
    },
    {
        "title": "AI টুলস দিয়ে সব কাজ ফ্রিতে",
        "lang": "bn",
        "text": (
            "আমি ২০২৬ সালে কোনো সফটওয়্যারের জন্য টাকা খরচ করি না।\n\n"
            "সব FREE AI টুলস দিয়ে করি।\n\n"
            "শুনলে অবাক হবেন:\n\n"
            "লেখালেখির জন্য:\n"
            "- Claude AI (free tier) - আর্টিকেল, ইমেইল, কপি সব\n"
            "- Notion AI - নোটস আর ডকুমেন্টেশন\n\n"
            "ডিজাইনের জন্য:\n"
            "- Canva AI - সোশ্যাল মিডিয়া পোস্ট\n"
            "- Ideogram - AI দিয়ে ছবি তৈরি\n\n"
            "ভিডিওর জন্য:\n"
            "- CapCut - AI দিয়ে ভিডিও এডিটিং\n"
            "- Descript - টেক্সট দিয়ে ভিডিও এডিট করুন\n\n"
            "রিসার্চের জন্য:\n"
            "- Perplexity - Google এর চেয়ে ভালো\n"
            "- NotebookLM - PDF আর ডকুমেন্ট অ্যানালাইসিস\n\n"
            "কোডিংয়ের জন্য:\n"
            "- Cursor - AI কোড এডিটর\n"
            "- Replit - ব্রাউজারে কোড করুন\n\n"
            "মাসিক সাশ্রয়: $500+\n"
            "মোট খরচ: $0\n\n"
            "এই পোস্টটা সেভ করে রাখুন।\n"
            "দরকার পড়বে।\n\n"
            "Inzamul Haque ফলো করুন।\n\n"
            "#AI #বাংলা #FreeTools #Tech"
        ),
    },
]


def get_thread_posts(count=2, lang=None):
    """Get thread-style engagement posts."""
    available = THREAD_POSTS.copy()
    if lang:
        available = [t for t in available if t["lang"] == lang]

    selected = random.sample(available, min(count, len(available)))
    posts = []

    for thread in selected:
        posts.append({
            "type": "thread",
            "text": thread["text"],
            "title": thread["title"],
            "lang": thread["lang"],
        })

    logger.info(f"[+] Generated {len(posts)} thread posts")
    return posts


def get_all_personal_content(ai_news_count=3, tips_count=3, thread_count=2):
    """Get all content mixed and shuffled."""
    from personal.content.ai_news import get_news_posts
    from personal.content.tips_generator import get_tips_posts

    all_posts = []
    all_posts.extend(get_news_posts(ai_news_count))
    all_posts.extend(get_tips_posts(tips_count))
    all_posts.extend(get_thread_posts(thread_count))

    random.shuffle(all_posts)
    logger.info(f"[+] Total content: {len(all_posts)} posts")
    return all_posts
