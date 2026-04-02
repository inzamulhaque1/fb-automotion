"""
Facebook Graph API Handler
============================
Handles video/image/text uploads to Facebook pages.
"""

import os
import time
import logging
import requests

from config.settings import FB_ACCESS_TOKEN, FB_GAMING_PAGE_ID, FB_PERSONAL_PAGE_ID

logger = logging.getLogger("FacebookAPI")

FB_GRAPH_URL = "https://graph.facebook.com/v25.0"


class FacebookAPI:
    """Facebook Graph API wrapper for page management."""

    def __init__(self, page_id, access_token=None):
        self.page_id = page_id
        self._user_token = access_token or FB_ACCESS_TOKEN
        self.base_url = f"{FB_GRAPH_URL}/{self.page_id}"
        # Auto-fetch page token from user token
        self.access_token = self._get_page_token()

    def _get_page_token(self):
        """Get page-specific access token (required for posting)."""
        # Method 1: Try direct page token fetch (works for pages not in me/accounts)
        try:
            url = f"{FB_GRAPH_URL}/{self.page_id}?fields=access_token&access_token={self._user_token}"
            response = requests.get(url)
            data = response.json()
            if "access_token" in data:
                logger.info(f"[+] Page token found (direct) for: {self.page_id}")
                return data["access_token"]
        except Exception as e:
            logger.warning(f"[!] Direct page token fetch failed: {e}")

        # Method 2: Fallback to me/accounts list
        try:
            url = f"{FB_GRAPH_URL}/me/accounts?limit=100"
            params = {"access_token": self._user_token}
            response = requests.get(url, params=params)
            data = response.json()

            if "data" in data:
                for page in data["data"]:
                    if page["id"] == self.page_id:
                        logger.info(f"[+] Page token found for: {page.get('name', self.page_id)}")
                        return page["access_token"]
        except Exception as e:
            logger.warning(f"[!] Could not fetch page token: {e}")

        logger.warning("[!] Using user token as fallback (may not work for posting)")
        return self._user_token

    def upload_video(self, video_path, title="", description=""):
        """
        Upload a video to Facebook page.

        Args:
            video_path: Path to video file
            title: Video title
            description: Video description/caption

        Returns:
            dict with upload result
        """
        if not os.path.exists(video_path):
            logger.error(f"Video not found: {video_path}")
            return {"error": "File not found"}

        file_size = os.path.getsize(video_path)
        logger.info(f"[*] Uploading video: {os.path.basename(video_path)} ({file_size / (1024*1024):.1f} MB)")

        # For large videos, use resumable upload
        if file_size > 50 * 1024 * 1024:  # > 50MB
            return self._resumable_upload(video_path, title, description)

        url = f"{FB_GRAPH_URL}/{self.page_id}/videos"

        with open(video_path, "rb") as f:
            files = {"source": f}
            data = {
                "access_token": self.access_token,
                "title": title,
                "description": description,
            }
            response = requests.post(url, data=data, files=files)

        result = response.json()
        if "id" in result:
            logger.info(f"[+] Video uploaded! ID: {result['id']}")
        else:
            logger.error(f"[!] Upload failed: {result}")

        return result

    def _resumable_upload(self, video_path, title, description):
        """Resumable upload for large videos."""
        file_size = os.path.getsize(video_path)

        # Step 1: Start upload session
        url = f"{FB_GRAPH_URL}/{self.page_id}/videos"
        data = {
            "access_token": self.access_token,
            "upload_phase": "start",
            "file_size": file_size,
        }
        response = requests.post(url, data=data)
        start_result = response.json()

        if "upload_session_id" not in start_result:
            return start_result

        session_id = start_result["upload_session_id"]

        # Step 2: Upload chunks
        chunk_size = 4 * 1024 * 1024  # 4MB chunks
        offset = 0

        with open(video_path, "rb") as f:
            while offset < file_size:
                chunk = f.read(chunk_size)
                data = {
                    "access_token": self.access_token,
                    "upload_phase": "transfer",
                    "upload_session_id": session_id,
                    "start_offset": offset,
                }
                files = {"video_file_chunk": chunk}
                response = requests.post(url, data=data, files=files)
                result = response.json()

                offset = int(result.get("start_offset", offset + len(chunk)))
                progress = min(100, (offset / file_size) * 100)
                logger.info(f"    Upload progress: {progress:.0f}%")

        # Step 3: Finish upload
        data = {
            "access_token": self.access_token,
            "upload_phase": "finish",
            "upload_session_id": session_id,
            "title": title,
            "description": description,
        }
        response = requests.post(url, data=data)
        return response.json()

    def post_text(self, message):
        """Post a text update to the page."""
        url = f"{self.base_url}/feed"
        data = {
            "access_token": self.access_token,
            "message": message,
        }
        response = requests.post(url, data=data)
        result = response.json()

        if "id" in result:
            logger.info(f"[+] Text post created! ID: {result['id']}")
        else:
            logger.error(f"[!] Post failed: {result}")

        return result

    def post_image(self, image_path, caption=""):
        """Post an image with caption to the page."""
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return {"error": "File not found"}

        url = f"{self.base_url}/photos"

        with open(image_path, "rb") as f:
            files = {"source": f}
            data = {
                "access_token": self.access_token,
                "message": caption,
            }
            response = requests.post(url, data=data, files=files)

        result = response.json()
        if "id" in result:
            logger.info(f"[+] Image posted! ID: {result['id']}")
        else:
            logger.error(f"[!] Image post failed: {result}")

        return result

    def schedule_post(self, message, scheduled_time, image_path=None):
        """
        Schedule a post for future publishing.

        Args:
            message: Post text
            scheduled_time: Unix timestamp (must be 10min-6months in future)
            image_path: Optional image to include
        """
        if image_path:
            url = f"{self.base_url}/photos"
            with open(image_path, "rb") as f:
                files = {"source": f}
                data = {
                    "access_token": self.access_token,
                    "message": message,
                    "scheduled_publish_time": int(scheduled_time),
                    "published": False,
                }
                response = requests.post(url, data=data, files=files)
        else:
            url = f"{self.base_url}/feed"
            data = {
                "access_token": self.access_token,
                "message": message,
                "scheduled_publish_time": int(scheduled_time),
                "published": False,
            }
            response = requests.post(url, data=data)

        result = response.json()
        if "id" in result:
            logger.info(f"[+] Post scheduled for {scheduled_time}! ID: {result['id']}")
        else:
            logger.error(f"[!] Schedule failed: {result}")

        return result

    def get_page_info(self):
        """Get page information."""
        url = self.base_url
        params = {
            "access_token": self.access_token,
            "fields": "name,fan_count,posts.limit(5){message,created_time}",
        }
        response = requests.get(url, params=params)
        return response.json()


def get_gaming_api():
    """Get Facebook API instance for gaming page."""
    return FacebookAPI(FB_GAMING_PAGE_ID)


def get_personal_api():
    """Get Facebook API instance for personal page."""
    return FacebookAPI(FB_PERSONAL_PAGE_ID)
