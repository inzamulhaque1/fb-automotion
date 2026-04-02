"""
FTP Server - iPhone to PC Video Transfer
=========================================
Start this server, connect from iPhone using any FTP app,
and videos will auto-land in input/raw_videos/
"""

import os
import logging
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

from config.settings import (
    FTP_HOST, FTP_PORT, FTP_USER, FTP_PASS, FTP_UPLOAD_DIR
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FTPServer")


def get_local_ip():
    """Get the local IP address for iPhone to connect."""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


class VideoFTPHandler(FTPHandler):
    """Custom FTP handler that logs video uploads."""

    def on_file_received(self, file):
        """Called when a file is fully uploaded."""
        ext = os.path.splitext(file)[1].lower()
        video_exts = {".mp4", ".mov", ".avi", ".mkv", ".m4v", ".webm"}
        if ext in video_exts:
            logger.info(f"[+] Video received: {os.path.basename(file)}")
            logger.info(f"    Size: {os.path.getsize(file) / (1024*1024):.1f} MB")
        else:
            logger.info(f"[*] File received: {os.path.basename(file)}")


def start_ftp_server():
    """Start the FTP server for iPhone video transfer."""
    os.makedirs(FTP_UPLOAD_DIR, exist_ok=True)

    authorizer = DummyAuthorizer()
    authorizer.add_user(
        FTP_USER, FTP_PASS, FTP_UPLOAD_DIR,
        perm="elradfmw"  # Full read/write permissions
    )

    handler = VideoFTPHandler
    handler.authorizer = authorizer
    handler.passive_ports = range(60000, 60100)
    handler.banner = "FB Automotion FTP Server - Ready for videos!"

    local_ip = get_local_ip()
    server = FTPServer((FTP_HOST, FTP_PORT), handler)
    server.max_cons = 5
    server.max_cons_per_ip = 3

    print("=" * 50)
    print("  FB Automotion - FTP Server")
    print("=" * 50)
    print(f"  Connect from iPhone:")
    print(f"  Host: {local_ip}")
    print(f"  Port: {FTP_PORT}")
    print(f"  User: {FTP_USER}")
    print(f"  Pass: {FTP_PASS}")
    print(f"  Upload Dir: {FTP_UPLOAD_DIR}")
    print("=" * 50)

    server.serve_forever()


if __name__ == "__main__":
    start_ftp_server()
