"""
FB Automotion - Web Dashboard
==============================
Control center for managing gaming & personal brand automation.
"""

import os
import json
import logging
import requests as http_requests
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO

from config.settings import (
    DASHBOARD_HOST, DASHBOARD_PORT, DASHBOARD_DEBUG,
    INPUT_DIR, OUTPUT_GAMING_DIR, OUTPUT_PERSONAL_DIR,
    GAMING, PERSONAL, BASE_DIR
)
from config.schedule import GAMING_SCHEDULE, PERSONAL_SCHEDULE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Dashboard")

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), "templates"),
            static_folder=os.path.join(os.path.dirname(__file__), "static"))
app.config["SECRET_KEY"] = "inz-automotion-2026"
socketio = SocketIO(app)

# Global state
automation_state = {
    "gaming": {
        "running": False,
        "videos_processed": 0,
        "videos_uploaded": 0,
        "videos_queued": 0,
        "last_upload": None,
    },
    "personal": {
        "running": False,
        "posts_created": 0,
        "posts_uploaded": 0,
        "posts_queued": 0,
        "last_post": None,
    },
    "ftp": {
        "running": False,
        "files_received": 0,
    },
}


def count_files(directory, extensions=None):
    """Count files in directory with optional extension filter."""
    if not os.path.exists(directory):
        return 0
    if extensions:
        return len([f for f in os.listdir(directory)
                    if os.path.splitext(f)[1].lower() in extensions])
    return len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])


# ============ Routes ============

@app.route("/")
def index():
    """Dashboard home page."""
    video_exts = {".mp4", ".mov", ".avi", ".mkv", ".m4v", ".webm"}
    stats = {
        "raw_videos": count_files(INPUT_DIR, video_exts),
        "gaming_ready": count_files(OUTPUT_GAMING_DIR, video_exts),
        "personal_ready": count_files(OUTPUT_PERSONAL_DIR),
        "gaming_config": GAMING,
        "personal_config": PERSONAL,
        "gaming_schedule": GAMING_SCHEDULE,
        "personal_schedule": PERSONAL_SCHEDULE,
        "state": automation_state,
    }
    return render_template("index.html", stats=stats)


@app.route("/gaming")
def gaming_page():
    """Gaming automation control page."""
    video_exts = {".mp4", ".mov", ".avi", ".mkv", ".m4v", ".webm"}
    raw_videos = []
    if os.path.exists(INPUT_DIR):
        raw_videos = [f for f in os.listdir(INPUT_DIR)
                      if os.path.splitext(f)[1].lower() in video_exts]

    processed_videos = []
    if os.path.exists(OUTPUT_GAMING_DIR):
        processed_videos = [f for f in os.listdir(OUTPUT_GAMING_DIR)
                           if os.path.splitext(f)[1].lower() in video_exts]

    return render_template("gaming.html",
                          raw_videos=raw_videos,
                          processed_videos=processed_videos,
                          config=GAMING,
                          schedule=GAMING_SCHEDULE,
                          state=automation_state["gaming"])


@app.route("/personal")
def personal_page():
    """Personal brand automation control page."""
    posts = []
    if os.path.exists(OUTPUT_PERSONAL_DIR):
        posts = os.listdir(OUTPUT_PERSONAL_DIR)

    return render_template("personal.html",
                          posts=posts,
                          config=PERSONAL,
                          schedule=PERSONAL_SCHEDULE,
                          state=automation_state["personal"])


@app.route("/settings")
def settings_page():
    """Settings page."""
    return render_template("settings.html",
                          gaming=GAMING,
                          personal=PERSONAL,
                          gaming_schedule=GAMING_SCHEDULE,
                          personal_schedule=PERSONAL_SCHEDULE)


# ============ API Endpoints ============

@app.route("/api/status")
def api_status():
    """Get current automation status."""
    video_exts = {".mp4", ".mov", ".avi", ".mkv", ".m4v", ".webm"}
    # Add FTP IP if running
    if automation_state["ftp"]["running"] and "ip" not in automation_state["ftp"]:
        from shared.ftp_server import get_local_ip
        automation_state["ftp"]["ip"] = get_local_ip()
    return jsonify({
        "state": automation_state,
        "raw_videos": count_files(INPUT_DIR, video_exts),
        "gaming_ready": count_files(OUTPUT_GAMING_DIR, video_exts),
        "personal_ready": count_files(OUTPUT_PERSONAL_DIR),
        "timestamp": datetime.now().isoformat(),
    })


@app.route("/api/gaming/start", methods=["POST"])
def start_gaming():
    """Start gaming automation."""
    automation_state["gaming"]["running"] = True
    socketio.emit("status_update", automation_state)
    logger.info("[*] Gaming automation started")
    return jsonify({"status": "started"})


@app.route("/api/gaming/stop", methods=["POST"])
def stop_gaming():
    """Stop gaming automation."""
    automation_state["gaming"]["running"] = False
    socketio.emit("status_update", automation_state)
    logger.info("[*] Gaming automation stopped")
    return jsonify({"status": "stopped"})


@app.route("/api/personal/start", methods=["POST"])
def start_personal():
    """Start personal brand automation."""
    automation_state["personal"]["running"] = True
    socketio.emit("status_update", automation_state)
    logger.info("[*] Personal automation started")
    return jsonify({"status": "started"})


@app.route("/api/personal/stop", methods=["POST"])
def stop_personal():
    """Stop personal brand automation."""
    automation_state["personal"]["running"] = False
    socketio.emit("status_update", automation_state)
    logger.info("[*] Personal automation stopped")
    return jsonify({"status": "stopped"})


@app.route("/api/ftp/start", methods=["POST"])
def start_ftp():
    """Start FTP server in background thread."""
    import threading
    from shared.ftp_server import start_ftp_server, get_local_ip

    if not automation_state["ftp"]["running"]:
        automation_state["ftp"]["running"] = True
        automation_state["ftp"]["ip"] = get_local_ip()
        thread = threading.Thread(target=start_ftp_server, daemon=True)
        thread.start()
        logger.info(f"[*] FTP Server started on {get_local_ip()}:2121")

    socketio.emit("status_update", automation_state)
    return jsonify({"status": "started", "ip": automation_state["ftp"].get("ip", "")})


@app.route("/api/ftp/stop", methods=["POST"])
def stop_ftp():
    """Stop FTP server."""
    automation_state["ftp"]["running"] = False
    socketio.emit("status_update", automation_state)
    return jsonify({"status": "stopped"})


@app.route("/mobile")
def mobile_upload():
    """Mobile-friendly video upload page."""
    return render_template("mobile.html")


@app.route("/api/upload/video", methods=["POST"])
def upload_video_api():
    """Handle video upload from mobile."""
    if "video" not in request.files:
        return jsonify({"status": "error", "message": "No video file"})

    file = request.files["video"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "No file selected"})

    # Save to input/raw_videos/
    os.makedirs(INPUT_DIR, exist_ok=True)
    filename = file.filename
    filepath = os.path.join(INPUT_DIR, filename)
    file.save(filepath)

    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    logger.info(f"[+] Video uploaded via mobile: {filename} ({size_mb:.1f} MB)")

    return jsonify({
        "status": "uploaded",
        "filename": filename,
        "size_mb": round(size_mb, 1),
    })


@app.route("/api/qrcode")
def get_qrcode():
    """Generate QR code for mobile upload page."""
    import qrcode
    import io
    from flask import send_file
    from shared.ftp_server import get_local_ip

    ip = get_local_ip()
    url = f"http://{ip}:{DASHBOARD_PORT}/mobile"

    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#ffffff", back_color="#0f0f0f")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return send_file(buf, mimetype="image/png")


@app.route("/api/mobile-url")
def get_mobile_url():
    """Get the mobile upload URL."""
    from shared.ftp_server import get_local_ip
    ip = get_local_ip()
    url = f"http://{ip}:{DASHBOARD_PORT}/mobile"
    return jsonify({"url": url, "ip": ip})


@app.route("/api/posts/all")
def get_all_posts():
    """Get all posts organized by day."""
    import sys
    sys.path.insert(0, BASE_DIR)
    from posts import POSTS

    posts_per_day = 10
    days = []
    for day_num in range(7):
        start = day_num * posts_per_day
        end = start + posts_per_day
        day_posts = []
        for i in range(start, min(end, len(POSTS))):
            preview = POSTS[i][:100] + "..." if len(POSTS[i]) > 100 else POSTS[i]
            day_posts.append({
                "index": i,
                "text": POSTS[i],
                "preview": preview,
            })
        if day_posts:
            days.append({
                "day": day_num + 1,
                "label": f"Day {day_num + 1}",
                "posts": day_posts,
                "count": len(day_posts),
            })

    return jsonify({"days": days, "total": len(POSTS)})


@app.route("/api/posts/edit", methods=["POST"])
def edit_post():
    """Edit a post by index."""
    import sys
    sys.path.insert(0, BASE_DIR)

    data = request.get_json()
    index = data.get("index")
    new_text = data.get("text", "").strip()

    if index is None or not new_text:
        return jsonify({"status": "error", "message": "Missing index or text"})

    # Read posts.py, find and replace the post
    posts_path = os.path.join(BASE_DIR, "posts.py")
    with open(posts_path, "r", encoding="utf-8") as f:
        content = f.read()

    from posts import POSTS
    if index < 0 or index >= len(POSTS):
        return jsonify({"status": "error", "message": "Invalid index"})

    old_text = POSTS[index]
    # Escape for replacement
    escaped_old = old_text.replace("\\", "\\\\").replace('"', '\\"')
    escaped_new = new_text.replace("\\", "\\\\").replace('"', '\\"')

    # Update in-memory
    POSTS[index] = new_text

    logger.info(f"[+] Post #{index + 1} edited")
    return jsonify({"status": "saved", "message": f"Post #{index + 1} updated!"})


@app.route("/api/posts/generate", methods=["POST"])
def generate_post_ai():
    """Generate a post using AI from a topic."""
    data = request.get_json()
    topic = data.get("topic", "").strip()
    lang = data.get("lang", "en")

    if not topic:
        return jsonify({"status": "error", "message": "Topic is empty"})

    # Use free AI API (Pollinations text API)
    if lang == "bn":
        prompt = (
            f"Write a Facebook post in proper Bangla (Bengali unicode) about: {topic}\n\n"
            f"Rules:\n"
            f"- Start with an engaging hook\n"
            f"- Use bullet points or numbered lists\n"
            f"- Keep it informative and valuable\n"
            f"- End with 'Inzamul Haque ফলো করুন।'\n"
            f"- Add 3-4 relevant hashtags with #বাংলা\n"
            f"- No links. No emojis overuse. Max 5 emojis.\n"
            f"- 150-300 words\n"
            f"- Write ONLY the post text, nothing else"
        )
    else:
        prompt = (
            f"Write a viral Facebook post about: {topic}\n\n"
            f"Rules:\n"
            f"- Start with a strong hook that stops scrolling\n"
            f"- Use bullet points or numbered lists\n"
            f"- Be informative, valuable, and engaging\n"
            f"- End with 'Follow Inzamul Haque' and relevant hashtags\n"
            f"- No links. Minimal emojis (max 3-4).\n"
            f"- 150-300 words\n"
            f"- Style: Like a tech influencer (Rene Remsik, Awa K. Penn)\n"
            f"- Write ONLY the post text, nothing else"
        )

    try:
        generated = None

        # Method 1: Gemini API
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if gemini_key:
            for model in ["gemini-2.0-flash-lite", "gemini-1.5-flash", "gemini-2.0-flash"]:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
                    payload = {
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"temperature": 0.9, "maxOutputTokens": 1024}
                    }
                    r = http_requests.post(url, json=payload, timeout=15)
                    data = r.json()
                    if "candidates" in data:
                        generated = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                        break
                except:
                    continue

        # Method 2: Groq free API (Llama 3)
        if not generated:
            try:
                groq_key = os.getenv("GROQ_API_KEY", "")
                if groq_key:
                    url = "https://api.groq.com/openai/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
                    payload = {
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.9, "max_tokens": 1024
                    }
                    r = http_requests.post(url, json=payload, headers=headers, timeout=15)
                    data = r.json()
                    if "choices" in data:
                        generated = data["choices"][0]["message"]["content"].strip()
            except:
                pass

        # Method 3: Pollinations (free, no key)
        if not generated:
            try:
                import urllib.parse
                api_url = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}?model=openai"
                r = http_requests.get(api_url, timeout=30)
                if r.status_code == 200 and len(r.text) > 50:
                    generated = r.text.strip()
            except:
                pass

        if generated:
            generated = generated.replace("```", "").strip()
            if generated.startswith('"') and generated.endswith('"'):
                generated = generated[1:-1]
            return jsonify({"status": "success", "text": generated})
        else:
            return jsonify({"status": "error", "message": "All AI providers busy. Try again in 30 seconds."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error: {str(e)}"})


@app.route("/api/posts/add", methods=["POST"])
def add_post():
    """Add a new post to posts.py."""
    data = request.get_json()
    new_text = data.get("text", "").strip()

    if not new_text:
        return jsonify({"status": "error", "message": "Post text is empty"})

    # Check duplicate
    import importlib
    import posts
    importlib.reload(posts)
    first_line = new_text.split('\n')[0][:50]
    for existing in posts.POSTS:
        if existing.split('\n')[0][:50] == first_line:
            return jsonify({"status": "error", "message": "This post already exists!"})

    # Add to file
    posts_path = os.path.join(BASE_DIR, "posts.py")
    with open(posts_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Build the new post entry with proper formatting
    lines = new_text.split('\n')
    formatted_lines = []
    for line in lines:
        escaped = line.replace('\\', '\\\\').replace('"', '\\"')
        formatted_lines.append(f'        "{escaped}\\n"')

    new_entry = '    # added\n    (\n' + '\n'.join(formatted_lines) + '\n    ),\n'

    last_bracket = content.rfind(']')
    if last_bracket == -1:
        return jsonify({"status": "error", "message": "Could not find posts list"})

    updated = content[:last_bracket] + new_entry + content[last_bracket:]

    with open(posts_path, "w", encoding="utf-8") as f:
        f.write(updated)

    importlib.reload(posts)

    logger.info(f"[+] New post added! Total: {len(posts.POSTS)}")
    return jsonify({"status": "saved", "message": f"Post added! Total: {len(posts.POSTS)}", "total": len(posts.POSTS)})


@app.route("/api/posts/<int:index>/post-now", methods=["POST"])
def post_specific_now(index):
    """Post a specific post by index to FB immediately."""
    import sys
    sys.path.insert(0, BASE_DIR)
    import config.settings as cfg
    from shared.fb_api import FacebookAPI
    from posts import POSTS

    if index < 0 or index >= len(POSTS):
        return jsonify({"status": "error", "message": "Invalid index"})

    page_id = cfg.FB_PERSONAL_PAGE_ID
    if not page_id or not cfg.FB_ACCESS_TOKEN:
        return jsonify({"status": "error", "message": "FB credentials not set"})

    api = FacebookAPI(page_id, cfg.FB_ACCESS_TOKEN)
    result = api.post_text(POSTS[index])

    if "id" in result:
        return jsonify({"status": "success", "message": "Posted!", "post_id": result["id"]})
    else:
        error_msg = result.get("error", {}).get("message", str(result))
        return jsonify({"status": "error", "message": f"Failed: {error_msg}"})


@app.route("/api/personal/posted")
def personal_posted():
    """Get posts that were actually posted to FB page."""
    import config.settings as cfg
    from shared.fb_api import FacebookAPI

    try:
        api = FacebookAPI(cfg.FB_PERSONAL_PAGE_ID, cfg.FB_ACCESS_TOKEN)
        url = f"https://graph.facebook.com/v25.0/{cfg.FB_PERSONAL_PAGE_ID}/feed"
        params = {
            "access_token": api.access_token,
            "fields": "message,created_time,permalink_url",
            "limit": 20,
        }
        r = http_requests.get(url, params=params)
        data = r.json()

        posts = []
        if "data" in data:
            for post in data["data"]:
                posts.append({
                    "id": post.get("id", ""),
                    "message": post.get("message", "(no text)")[:200],
                    "time": post.get("created_time", ""),
                    "link": post.get("permalink_url", ""),
                })

        return jsonify({"posts": posts, "count": len(posts)})
    except Exception as e:
        return jsonify({"posts": [], "count": 0, "error": str(e)})


@app.route("/api/personal/pending")
def personal_pending():
    """Get pending personal posts with preview."""
    import sys
    sys.path.insert(0, BASE_DIR)
    from personal.content.post_writer import get_all_personal_content

    try:
        posts = get_all_personal_content(ai_news_count=3, tips_count=3, thread_count=2)
        return jsonify({"posts": posts, "count": len(posts)})
    except Exception as e:
        return jsonify({"posts": [], "count": 0, "error": str(e)})


@app.route("/api/settings/facebook", methods=["POST"])
def save_fb_settings():
    """Save Facebook credentials to .env file."""
    data = request.get_json()
    token = data.get("access_token", "").strip()
    gaming_id = data.get("gaming_page_id", "").strip()
    personal_id = data.get("personal_page_id", "").strip()

    env_path = os.path.join(BASE_DIR, ".env")

    # Read current .env
    env_lines = {}
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    env_lines[key.strip()] = val.strip()

    # Update values
    if token:
        env_lines["FB_ACCESS_TOKEN"] = token
    if gaming_id:
        env_lines["FB_GAMING_PAGE_ID"] = gaming_id
    if personal_id:
        env_lines["FB_PERSONAL_PAGE_ID"] = personal_id

    # Write back
    with open(env_path, "w") as f:
        f.write("# Facebook API Credentials\n")
        f.write(f"FB_ACCESS_TOKEN={env_lines.get('FB_ACCESS_TOKEN', '')}\n")
        f.write(f"FB_GAMING_PAGE_ID={env_lines.get('FB_GAMING_PAGE_ID', '')}\n")
        f.write(f"FB_PERSONAL_PAGE_ID={env_lines.get('FB_PERSONAL_PAGE_ID', '')}\n")
        f.write(f"\n# FTP Credentials\n")
        f.write(f"FTP_USER={env_lines.get('FTP_USER', 'inzamul')}\n")
        f.write(f"FTP_PASS={env_lines.get('FTP_PASS', 'automotion2026')}\n")

    # Reload into settings
    import config.settings as cfg
    if token:
        cfg.FB_ACCESS_TOKEN = token
    if gaming_id:
        cfg.FB_GAMING_PAGE_ID = gaming_id
    if personal_id:
        cfg.FB_PERSONAL_PAGE_ID = personal_id

    logger.info("[+] Facebook settings saved!")
    return jsonify({"status": "saved", "message": "Facebook settings saved successfully!"})


@app.route("/api/settings/facebook", methods=["GET"])
def get_fb_settings():
    """Get current Facebook settings (masked token)."""
    import config.settings as cfg
    token = cfg.FB_ACCESS_TOKEN
    masked = ""
    if token and token != "your_access_token_here":
        masked = token[:8] + "..." + token[-4:] if len(token) > 12 else "****"

    return jsonify({
        "has_token": bool(token and token != "your_access_token_here"),
        "masked_token": masked,
        "gaming_page_id": cfg.FB_GAMING_PAGE_ID if cfg.FB_GAMING_PAGE_ID != "your_gaming_page_id_here" else "",
        "personal_page_id": cfg.FB_PERSONAL_PAGE_ID if cfg.FB_PERSONAL_PAGE_ID != "your_personal_page_id_here" else "",
    })


@app.route("/api/test-post", methods=["POST"])
def test_post():
    """Send a test post to verify connection."""
    data = request.get_json()
    page_type = data.get("page", "personal")  # "personal" or "gaming"

    import config.settings as cfg
    from shared.fb_api import FacebookAPI

    if page_type == "personal":
        page_id = cfg.FB_PERSONAL_PAGE_ID
    else:
        page_id = cfg.FB_GAMING_PAGE_ID

    if not page_id or page_id.startswith("your_"):
        return jsonify({"status": "error", "message": f"{page_type} Page ID not set! Go to Settings first."})

    if not cfg.FB_ACCESS_TOKEN or cfg.FB_ACCESS_TOKEN.startswith("your_"):
        return jsonify({"status": "error", "message": "Access Token not set! Go to Settings first."})

    api = FacebookAPI(page_id, cfg.FB_ACCESS_TOKEN)

    # Use custom message if provided, otherwise default test message
    custom_msg = data.get("message", "")
    message = custom_msg if custom_msg else (
        f"✅ FB Automotion connected successfully!\n\n"
        f"This is a test post from the automation system.\n"
        f"🤖 Automated by FB Automotion\n\n"
        f"#FBAutomotion #Test"
    )
    result = api.post_text(message)

    if "id" in result:
        return jsonify({"status": "success", "message": "Test post sent! Check your Facebook page.", "post_id": result["id"]})
    else:
        error_msg = result.get("error", {}).get("message", str(result))
        return jsonify({"status": "error", "message": f"Failed: {error_msg}"})


@app.route("/api/videos/raw")
def list_raw_videos():
    """List raw videos in input folder."""
    video_exts = {".mp4", ".mov", ".avi", ".mkv", ".m4v", ".webm"}
    videos = []
    if os.path.exists(INPUT_DIR):
        for f in os.listdir(INPUT_DIR):
            if os.path.splitext(f)[1].lower() in video_exts:
                filepath = os.path.join(INPUT_DIR, f)
                videos.append({
                    "name": f,
                    "size_mb": round(os.path.getsize(filepath) / (1024 * 1024), 1),
                    "modified": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
                })
    return jsonify(videos)


@app.route("/api/videos/processed")
def list_processed_videos():
    """List processed gaming videos."""
    video_exts = {".mp4", ".mov", ".avi", ".mkv", ".m4v", ".webm"}
    videos = []
    if os.path.exists(OUTPUT_GAMING_DIR):
        for f in os.listdir(OUTPUT_GAMING_DIR):
            if os.path.splitext(f)[1].lower() in video_exts:
                filepath = os.path.join(OUTPUT_GAMING_DIR, f)
                videos.append({
                    "name": f,
                    "size_mb": round(os.path.getsize(filepath) / (1024 * 1024), 1),
                    "modified": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
                })
    return jsonify(videos)


# ============ SocketIO Events ============

@socketio.on("connect")
def handle_connect():
    """Client connected."""
    socketio.emit("status_update", automation_state)


def update_state(module, key, value):
    """Update state and notify all clients."""
    automation_state[module][key] = value
    socketio.emit("status_update", automation_state)


# ============ Start Server ============

def start_dashboard():
    """Start the web dashboard."""
    print("=" * 50)
    print("  FB Automotion - Dashboard")
    print(f"  http://localhost:{DASHBOARD_PORT}")
    print("=" * 50)
    socketio.run(app, host=DASHBOARD_HOST, port=DASHBOARD_PORT,
                 debug=DASHBOARD_DEBUG, allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    start_dashboard()
