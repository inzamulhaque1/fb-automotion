"""
Personal Brand Uploader - Post content to FB page
====================================================
Uploads text posts, image cards, and threads to Inzamul Haque page.
"""

import os
import logging
from shared.fb_api import get_personal_api
from config.settings import OUTPUT_PERSONAL_DIR

logger = logging.getLogger("PersonalUploader")


def upload_text_post(post_data):
    """
    Upload a text post to personal page.

    Args:
        post_data: Dict with 'text' key

    Returns:
        Upload result dict
    """
    api = get_personal_api()
    text = post_data.get("text", "")

    if not text:
        logger.warning("[!] Empty post text, skipping")
        return {"error": "Empty text"}

    logger.info(f"[*] Posting: {post_data.get('title', 'text post')[:50]}...")
    result = api.post_text(text)
    return result


def upload_image_post(image_path, caption=""):
    """
    Upload an image post to personal page.

    Args:
        image_path: Path to image file
        caption: Post caption

    Returns:
        Upload result dict
    """
    api = get_personal_api()

    if not os.path.exists(image_path):
        logger.error(f"[!] Image not found: {image_path}")
        return {"error": "File not found"}

    logger.info(f"[*] Posting image: {os.path.basename(image_path)}")
    result = api.post_image(image_path, caption=caption)

    if "id" in result:
        # Move to posted folder
        posted_dir = os.path.join(OUTPUT_PERSONAL_DIR, "posted")
        os.makedirs(posted_dir, exist_ok=True)
        dest = os.path.join(posted_dir, os.path.basename(image_path))
        os.rename(image_path, dest)

    return result


def upload_content(post_data):
    """
    Upload any type of content based on post type.

    Args:
        post_data: Dict with type, text, and optional image_path

    Returns:
        Upload result
    """
    post_type = post_data.get("type", "text")

    if post_type in ("ai_news", "web_dev_tip", "thread"):
        # Text-only posts
        return upload_text_post(post_data)

    elif post_type == "image_card":
        # Image with caption
        image_path = post_data.get("image_path", "")
        caption = post_data.get("text", "")
        return upload_image_post(image_path, caption)

    else:
        return upload_text_post(post_data)


def upload_all_pending(posts):
    """
    Upload a list of posts.

    Args:
        posts: List of post dicts

    Returns:
        List of results
    """
    results = []
    for post in posts:
        result = upload_content(post)
        results.append(result)

    success = sum(1 for r in results if "id" in r)
    logger.info(f"[+] Uploaded {success}/{len(results)} posts")
    return results
