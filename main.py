"""
FB Automotion - Main Entry Point
==================================
INZ-Gaming + Inzamul Haque Facebook Page Automation

Usage:
    python main.py              # Start everything (dashboard + automation)
    python main.py --dashboard  # Start only dashboard
    python main.py --ftp        # Start only FTP server
    python main.py --gaming     # Start only gaming automation
    python main.py --personal   # Start only personal automation
"""

import sys
import os
import signal
import logging
import threading
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import DASHBOARD_PORT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("Main")


def print_banner():
    """Print startup banner."""
    print()
    print("=" * 55)
    print("  FB AUTOMOTION")
    print("  INZ-Gaming  |  Inzamul Haque")
    print("  Facebook Page Automation System")
    print("=" * 55)
    print()


def start_ftp_server():
    """Start FTP server in a thread."""
    from shared.ftp_server import start_ftp_server
    logger.info("[*] Starting FTP Server...")
    thread = threading.Thread(target=start_ftp_server, daemon=True)
    thread.start()
    return thread


def start_file_watcher():
    """Start file watcher with gaming pipeline callback."""
    from shared.file_watcher import start_watcher
    from gaming.editor.pipeline import process_video

    def on_new_video(video_path):
        logger.info(f"[*] New video detected, processing: {os.path.basename(video_path)}")
        try:
            results = process_video(video_path)
            logger.info(f"[+] Processed {len(results)} clips from {os.path.basename(video_path)}")
        except Exception as e:
            logger.error(f"[!] Processing failed: {e}")

    logger.info("[*] Starting File Watcher...")
    thread = threading.Thread(target=start_watcher, args=(on_new_video,), daemon=True)
    thread.start()
    return thread


def start_gaming_scheduler():
    """Start gaming upload scheduler."""
    from gaming.scheduler import GamingScheduler

    scheduler = GamingScheduler()
    scheduler.start()
    logger.info("[*] Gaming scheduler running")
    return scheduler


def start_personal_scheduler():
    """Start personal brand scheduler."""
    from personal.scheduler import PersonalScheduler

    scheduler = PersonalScheduler()
    scheduler.start()
    logger.info("[*] Personal scheduler running")
    return scheduler


def start_dashboard():
    """Start web dashboard."""
    from dashboard.app import start_dashboard
    logger.info(f"[*] Dashboard: http://localhost:{DASHBOARD_PORT}")
    start_dashboard()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="FB Automotion System")
    parser.add_argument("--dashboard", action="store_true", help="Start only dashboard")
    parser.add_argument("--ftp", action="store_true", help="Start only FTP server")
    parser.add_argument("--gaming", action="store_true", help="Start only gaming automation")
    parser.add_argument("--personal", action="store_true", help="Start only personal automation")
    parser.add_argument("--all", action="store_true", help="Start everything")
    args = parser.parse_args()

    print_banner()

    # If no specific flag, start everything
    start_all = not any([args.dashboard, args.ftp, args.gaming, args.personal])

    if start_all or args.all:
        logger.info("[*] Starting FULL automation system...")
        print()

        # 1. FTP Server
        start_ftp_server()
        logger.info("[✓] FTP Server started")

        # 2. File Watcher (auto-process new videos)
        start_file_watcher()
        logger.info("[✓] File Watcher started")

        # 3. Gaming Scheduler
        gaming_sched = start_gaming_scheduler()
        logger.info("[✓] Gaming Scheduler started")

        # 4. Personal Scheduler
        personal_sched = start_personal_scheduler()
        logger.info("[✓] Personal Scheduler started")

        print()
        logger.info("[*] All systems running!")
        logger.info(f"[*] Dashboard: http://localhost:{DASHBOARD_PORT}")
        print()

        # 5. Dashboard (blocks - runs Flask server)
        start_dashboard()

    elif args.dashboard:
        logger.info("[*] Starting Dashboard only...")
        start_dashboard()

    elif args.ftp:
        logger.info("[*] Starting FTP Server only...")
        from shared.ftp_server import start_ftp_server as run_ftp
        run_ftp()

    elif args.gaming:
        logger.info("[*] Starting Gaming automation only...")
        start_ftp_server()
        start_file_watcher()
        gaming_sched = start_gaming_scheduler()
        logger.info("[*] Gaming automation running. Press Ctrl+C to stop.")
        try:
            signal.pause() if hasattr(signal, 'pause') else input("Press Enter to stop...\n")
        except (KeyboardInterrupt, EOFError):
            gaming_sched.stop()

    elif args.personal:
        logger.info("[*] Starting Personal automation only...")
        personal_sched = start_personal_scheduler()
        logger.info("[*] Personal automation running. Press Ctrl+C to stop.")
        try:
            signal.pause() if hasattr(signal, 'pause') else input("Press Enter to stop...\n")
        except (KeyboardInterrupt, EOFError):
            personal_sched.stop()


if __name__ == "__main__":
    main()
