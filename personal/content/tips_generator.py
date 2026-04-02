"""
AI Tools & Resources Posts - Influencer style
================================================
Tool recommendations, free courses, AI hacks.
NOT basic coding tips - these are viral-style value posts.
"""

import random
import logging

logger = logging.getLogger("TipsGenerator")

# Viral-style AI/Tech posts (like Rene Remsik, Awa K. Penn)
VIRAL_POSTS = [
    {
        "title": "7 Free AI Tools That Replace $500/month Software",
        "text": (
            "Stop paying for software. These 7 FREE AI tools do the same job:\n\n"
            "1. ChatGPT + Claude - Replace your $200/month copywriter\n"
            "2. Canva AI - Replace your $50/month designer\n"
            "3. Gamma.app - Replace your $30/month presentation tool\n"
            "4. Descript - Replace your $40/month video editor\n"
            "5. Notion AI - Replace your $20/month project manager\n"
            "6. Perplexity - Replace your research assistant\n"
            "7. v0.dev - Replace your $100/month UI developer\n\n"
            "Total saved: $500+/month\n"
            "Total cost: $0\n\n"
            "Save this post. You'll need it.\n\n"
            "Follow Inzamul Haque for more AI hacks.\n\n"
            "#AI #AITools #FreeTools #Productivity #Tech"
        ),
        "type": "tools_list",
    },
    {
        "title": "5 AI Side Hustles Making People $3000+/month",
        "text": (
            "5 AI side hustles that are making people $3000+/month in 2026:\n\n"
            "1. AI Content Agency\n"
            "   - Use Claude/ChatGPT to write content\n"
            "   - Charge $500-2000/client\n"
            "   - 5 clients = $5000/month\n\n"
            "2. AI Thumbnail Design\n"
            "   - Use Midjourney + Canva\n"
            "   - YouTubers pay $20-50/thumbnail\n"
            "   - 100 thumbnails = $3000/month\n\n"
            "3. AI Chatbot Builder\n"
            "   - Build chatbots for businesses\n"
            "   - Charge $500-1500 per bot\n"
            "   - Low effort, high demand\n\n"
            "4. AI Course Creator\n"
            "   - Create courses with AI help\n"
            "   - Sell on Udemy/Gumroad\n"
            "   - Passive income potential\n\n"
            "5. AI Automation Consultant\n"
            "   - Automate business workflows\n"
            "   - Charge $1000-3000/project\n"
            "   - Every business needs this\n\n"
            "The best time to start was yesterday.\n"
            "The second best time is NOW.\n\n"
            "Follow Inzamul Haque for more AI money tips.\n\n"
            "#AI #SideHustle #MakeMoneyOnline #AIBusiness"
        ),
        "type": "money_tips",
    },
    {
        "title": "Claude vs ChatGPT vs Gemini - Which One Wins in 2026?",
        "text": (
            "I tested all 3 AI models for a week. Here's my honest review:\n\n"
            "CLAUDE (Anthropic):\n"
            "- Best for: Coding, analysis, long documents\n"
            "- Writing quality: 9/10\n"
            "- Coding: 10/10\n"
            "- Verdict: Best for developers\n\n"
            "CHATGPT (OpenAI):\n"
            "- Best for: General tasks, plugins, image generation\n"
            "- Writing quality: 8/10\n"
            "- Ecosystem: 10/10\n"
            "- Verdict: Best all-rounder\n\n"
            "GEMINI (Google):\n"
            "- Best for: Research, Google integration\n"
            "- Multimodal: 9/10\n"
            "- Integration: 10/10\n"
            "- Verdict: Best for Google users\n\n"
            "My recommendation:\n"
            "Use Claude for work. ChatGPT for creativity. Gemini for research.\n\n"
            "Agree or disagree? Comment below.\n\n"
            "Follow Inzamul Haque for AI comparisons.\n\n"
            "#AI #ChatGPT #Claude #Gemini #AIComparison"
        ),
        "type": "comparison",
    },
    {
        "title": "10 AI Websites You Should Bookmark Right Now",
        "text": (
            "10 AI websites that will make you 10x more productive:\n\n"
            "1. perplexity.ai - AI search (goodbye Google)\n"
            "2. gamma.app - Create presentations in seconds\n"
            "3. claude.ai - Best AI for coding & writing\n"
            "4. v0.dev - Generate UI code from text\n"
            "5. ideogram.ai - Generate images for free\n"
            "6. notebooklm.google - AI research assistant\n"
            "7. suno.ai - Create music with AI\n"
            "8. descript.com - Edit video like editing text\n"
            "9. heygen.com - AI video avatars\n"
            "10. replit.com - Build apps without coding\n\n"
            "Bookmark this post. Come back when you need it.\n\n"
            "Which one is your favorite? Comment below.\n\n"
            "Follow Inzamul Haque for daily AI tools.\n\n"
            "#AI #AITools #Productivity #Tech #Websites"
        ),
        "type": "tools_list",
    },
    {
        "title": "You Don't Need a CS Degree in 2026",
        "text": (
            "Unpopular opinion: You don't need a CS degree in 2026.\n\n"
            "Here's what you need instead:\n\n"
            "1. Learn to use AI tools (Claude, ChatGPT, Cursor)\n"
            "2. Build 5 real projects (not todo apps)\n"
            "3. Learn prompt engineering\n"
            "4. Understand APIs and how systems connect\n"
            "5. Build an online presence (like this page)\n\n"
            "Companies don't care about your degree.\n"
            "They care about what you can BUILD.\n\n"
            "I've seen people with no degree get $80K+ jobs because:\n"
            "- They had a strong portfolio\n"
            "- They knew how to use AI effectively\n"
            "- They could solve real problems\n\n"
            "Stop collecting certificates.\n"
            "Start building things.\n\n"
            "Follow Inzamul Haque for real tech advice.\n\n"
            "#Tech #Career #NoDegree #AI #WebDev"
        ),
        "type": "opinion",
    },
    {
        "title": "How I Would Learn AI in 2026 (If Starting From Zero)",
        "text": (
            "If I had to learn AI from scratch in 2026, here's my exact plan:\n\n"
            "Week 1-2: Understand the basics\n"
            "- What is AI, ML, Deep Learning?\n"
            "- Play with ChatGPT, Claude, Gemini\n"
            "- No coding needed yet\n\n"
            "Week 3-4: Learn Python basics\n"
            "- Variables, loops, functions\n"
            "- Free on YouTube (CS50 Python)\n\n"
            "Month 2: Prompt Engineering\n"
            "- Learn to talk to AI effectively\n"
            "- This alone is a career skill\n"
            "- Practice daily\n\n"
            "Month 3: Build AI apps\n"
            "- Use Claude API / OpenAI API\n"
            "- Build a chatbot\n"
            "- Build an automation tool\n\n"
            "Month 4-6: Specialize\n"
            "- Pick: AI agents, RAG, or fine-tuning\n"
            "- Build a portfolio\n"
            "- Start freelancing\n\n"
            "6 months. Zero to job-ready.\n"
            "The only thing stopping you is starting.\n\n"
            "Follow Inzamul Haque for AI learning tips.\n\n"
            "#AI #LearnAI #MachineLearning #Career #Tech"
        ),
        "type": "roadmap",
    },
    {
        "title": "OpenAI Just Made Every Developer's Job Easier",
        "text": (
            "OpenAI just released something that changes everything for developers.\n\n"
            "What happened:\n"
            "- New API features that cut development time by 50%\n"
            "- Better function calling\n"
            "- Cheaper pricing\n"
            "- Multi-modal support built in\n\n"
            "What this means for YOU:\n"
            "- Building AI apps is now easier than ever\n"
            "- You can build what took teams months, alone, in days\n"
            "- If you're not using AI in your workflow, you're already behind\n\n"
            "The developers who adapt will thrive.\n"
            "The ones who don't will struggle.\n\n"
            "Which side are you on?\n\n"
            "Follow Inzamul Haque for AI developer news.\n\n"
            "#AI #Developer #OpenAI #Programming #Tech"
        ),
        "type": "news_opinion",
    },
    {
        "title": "AI Will NOT Replace You. But Someone Using AI Will.",
        "text": (
            "Let me be real with you.\n\n"
            "AI is not coming for your job.\n"
            "But someone who knows how to use AI IS.\n\n"
            "Think about it:\n"
            "- A designer using AI creates 10x more designs\n"
            "- A developer using AI writes code 5x faster\n"
            "- A marketer using AI runs campaigns 3x more efficiently\n\n"
            "The question isn't 'Will AI take my job?'\n"
            "The question is 'Am I using AI to be better at my job?'\n\n"
            "3 things you should do TODAY:\n"
            "1. Sign up for Claude or ChatGPT (both have free tiers)\n"
            "2. Use AI for your daily work tasks\n"
            "3. Learn prompt engineering (it's a superpower)\n\n"
            "The future belongs to people who work WITH AI.\n"
            "Not against it.\n\n"
            "Follow Inzamul Haque for AI insights.\n\n"
            "#AI #FutureOfWork #Productivity #Tech #Career"
        ),
        "type": "motivation",
    },
    {
        "title": "5 Free AI Courses That Are Better Than Any $2000 Bootcamp",
        "text": (
            "You don't need to pay thousands for AI education in 2026.\n\n"
            "These 5 FREE courses will teach you everything:\n\n"
            "1. DeepLearning.AI - Andrew Ng\n"
            "   - AI for Everyone (Coursera)\n"
            "   - Best starting point\n\n"
            "2. fast.ai - Practical Deep Learning\n"
            "   - Hands-on, project-based\n"
            "   - You'll build real AI apps\n\n"
            "3. Google AI Essentials\n"
            "   - Learn directly from Google\n"
            "   - Certificate included\n\n"
            "4. Microsoft AI Fundamentals\n"
            "   - Azure AI certification prep\n"
            "   - Industry recognized\n\n"
            "5. Hugging Face NLP Course\n"
            "   - Best for language AI\n"
            "   - Open source community\n\n"
            "Total cost: $0\n"
            "Total value: Priceless\n\n"
            "Save this post. Start learning today.\n\n"
            "Follow Inzamul Haque for free AI resources.\n\n"
            "#AI #FreeCourses #Learning #Education #Tech"
        ),
        "type": "courses",
    },
    {
        "title": "I Automated My Entire Workflow With AI. Here's How.",
        "text": (
            "I used to spend 8 hours on tasks that now take me 30 minutes.\n\n"
            "Here's exactly what I automated:\n\n"
            "Content Writing:\n"
            "Before: 2 hours per article\n"
            "Now: 15 minutes with Claude\n\n"
            "Social Media:\n"
            "Before: 1 hour daily posting\n"
            "Now: Fully automated (like this post)\n\n"
            "Research:\n"
            "Before: 3 hours of Googling\n"
            "Now: 5 minutes with Perplexity\n\n"
            "Code Reviews:\n"
            "Before: 45 min per PR\n"
            "Now: 10 min with AI assistance\n\n"
            "Email:\n"
            "Before: 1 hour responding\n"
            "Now: AI drafts, I review\n\n"
            "Time saved: 6+ hours DAILY\n\n"
            "The tools I use:\n"
            "- Claude for writing & coding\n"
            "- Perplexity for research\n"
            "- Zapier for automation\n"
            "- Custom Python scripts\n\n"
            "Start automating. Stop wasting time.\n\n"
            "Follow Inzamul Haque for automation tips.\n\n"
            "#AI #Automation #Productivity #TimeManagement"
        ),
        "type": "personal_story",
    },
]

# Bangla viral posts
BANGLA_POSTS = [
    {
        "title": "৫টি AI টুল যা আপনার জানা দরকার",
        "text": (
            "২০২৬ সালে এই ৫টি AI টুল না জানলে আপনি পিছিয়ে পড়বেন:\n\n"
            "১. Claude AI - কোডিং আর লেখালেখির জন্য সেরা\n"
            "   - ফ্রি তে ব্যবহার করা যায়\n"
            "   - ChatGPT এর চেয়ে ভালো লেখে\n\n"
            "২. Perplexity AI - Google এর বিকল্প\n"
            "   - সার্চ করুন, সরাসরি উত্তর পান\n"
            "   - স্টুডেন্টদের জন্য অসাধারণ\n\n"
            "৩. Gamma App - ৩০ সেকেন্ডে প্রেজেন্টেশন\n"
            "   - টপিক লিখুন, প্রেজেন্টেশন রেডি\n"
            "   - অফিসের প্রেজেন্টেশন নিয়ে আর টেনশন নেই\n\n"
            "৪. v0.dev - কোডিং ছাড়াই ওয়েবসাইট বানান\n"
            "   - বলুন কি চান, কোড রেডি\n"
            "   - ফ্রিল্যান্সিংয়ে ব্যবহার করুন\n\n"
            "৫. Suno AI - AI দিয়ে গান বানান\n"
            "   - লিরিক্স লিখুন, গান রেডি\n"
            "   - YouTube ভিডিওর ব্যাকগ্রাউন্ড মিউজিক\n\n"
            "এই ৫টি টুল শিখে নিন - আপনার ক্যারিয়ার বদলে যাবে।\n\n"
            "Inzamul Haque ফলো করুন প্রতিদিনের AI আপডেটের জন্য।\n\n"
            "#AI #বাংলা #AITools #Tech"
        ),
        "type": "tools_bangla",
    },
    {
        "title": "AI তে ক্যারিয়ার গড়ুন",
        "text": (
            "সংক্ষেপে বলি, বড় প্রভাব:\n\n"
            "AI শিখুন। ক্যারিয়ার বদলে ফেলুন।\n\n"
            "বাংলাদেশে এখন AI ডেভেলপারদের চাহিদা বাড়ছে।\n"
            "বেতন: ৫০,০০০ - ২,০০,০০০ টাকা/মাস\n"
            "রিমোট জব: অসীম সুযোগ\n\n"
            "কি করতে হবে?\n"
            "১. Python শিখুন (২ মাস)\n"
            "২. AI টুলস ব্যবহার শিখুন (১ মাস)\n"
            "৩. প্রজেক্ট বানান (২ মাস)\n"
            "৪. ফ্রিল্যান্সিং শুরু করুন\n\n"
            "৬ মাসে আপনার আয় দ্বিগুণ হবে।\n"
            "এটা প্রতিশ্রুতি না, বাস্তবতা।\n\n"
            "কিন্তু শুরু তো করতে হবে।\n\n"
            "কমেন্টে 'START' লিখুন যদি সিরিয়াসলি শিখতে চান।\n"
            "আমি গাইড করবো।\n\n"
            "Follow Inzamul Haque\n\n"
            "#AI #বাংলাদেশ #ক্যারিয়ার #টেক"
        ),
        "type": "career_bangla",
    },
]


def get_tips_posts(count=3):
    """Get viral-style influencer posts."""
    selected = random.sample(VIRAL_POSTS, min(count, len(VIRAL_POSTS)))
    posts = []

    for tip in selected:
        posts.append({
            "type": "viral_post",
            "text": tip["text"],
            "title": tip["title"],
            "category": tip.get("type", "general"),
        })

    # Add one Bangla post
    if count > 2 and BANGLA_POSTS:
        bn = random.choice(BANGLA_POSTS)
        posts.append({
            "type": "viral_post",
            "text": bn["text"],
            "title": bn["title"],
            "category": "bangla",
        })

    logger.info(f"[+] Generated {len(posts)} viral posts")
    return posts
