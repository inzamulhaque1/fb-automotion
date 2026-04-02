"""
Facebook Token Manager
========================
Exchanges short-lived token for long-lived (60 day) token.
Also gets permanent page tokens from long-lived user token.

Usage:
  python shared/token_manager.py --exchange
  python shared/token_manager.py --check
  python shared/token_manager.py --page-tokens
"""

import os
import sys
import json
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv, set_key

load_dotenv()

FB_GRAPH_URL = "https://graph.facebook.com/v25.0"
ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")


def check_token():
    """Check current token validity and expiry."""
    token = os.getenv("FB_ACCESS_TOKEN", "")
    if not token:
        print("[!] No FB_ACCESS_TOKEN found in .env")
        return None

    url = f"{FB_GRAPH_URL}/debug_token"
    params = {"input_token": token, "access_token": token}

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json().get("data", {})

        is_valid = data.get("is_valid", False)
        expires_at = data.get("expires_at", 0)
        app_id = data.get("app_id", "")
        token_type = data.get("type", "")

        if expires_at:
            expiry = datetime.fromtimestamp(expires_at, tz=timezone.utc)
            remaining = expiry - datetime.now(timezone.utc)
            days_left = remaining.days
        else:
            expiry = None
            days_left = "never (permanent)"

        print(f"[*] Token Status:")
        print(f"    Valid: {is_valid}")
        print(f"    Type: {token_type}")
        print(f"    App ID: {app_id}")
        if expiry:
            print(f"    Expires: {expiry.strftime('%Y-%m-%d %H:%M UTC')}")
            print(f"    Days left: {days_left}")
        else:
            print(f"    Expires: Never (permanent page token)")

        return {
            "valid": is_valid,
            "expires_at": expires_at,
            "days_left": days_left,
            "app_id": app_id,
            "type": token_type,
        }
    except Exception as e:
        print(f"[!] Error checking token: {e}")
        return None


def exchange_for_long_lived(app_id=None, app_secret=None):
    """Exchange short-lived token for long-lived (60 day) token."""
    token = os.getenv("FB_ACCESS_TOKEN", "")
    if not app_id:
        app_id = os.getenv("FB_APP_ID", "")
    if not app_secret:
        app_secret = os.getenv("FB_APP_SECRET", "")

    if not token:
        print("[!] No FB_ACCESS_TOKEN in .env")
        return None
    if not app_id or not app_secret:
        print("[!] Need FB_APP_ID and FB_APP_SECRET.")
        print("    Get them from: https://developers.facebook.com/apps/")
        print("    Then add to .env:")
        print("    FB_APP_ID=your_app_id")
        print("    FB_APP_SECRET=your_app_secret")
        return None

    url = f"{FB_GRAPH_URL}/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": token,
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        if "access_token" in data:
            new_token = data["access_token"]
            expires_in = data.get("expires_in", 0)
            days = expires_in // 86400 if expires_in else 60

            print(f"[+] Long-lived token obtained! Expires in ~{days} days")

            # Save to .env
            set_key(ENV_FILE, "FB_ACCESS_TOKEN", new_token)
            print(f"[+] Token saved to .env")

            return new_token
        else:
            error = data.get("error", {})
            print(f"[!] Exchange failed: {error.get('message', data)}")
            return None
    except Exception as e:
        print(f"[!] Error: {e}")
        return None


def get_page_tokens():
    """Get permanent page tokens (from long-lived user token)."""
    token = os.getenv("FB_ACCESS_TOKEN", "")
    if not token:
        print("[!] No FB_ACCESS_TOKEN")
        return {}

    url = f"{FB_GRAPH_URL}/me/accounts"
    params = {"access_token": token, "fields": "id,name,access_token"}

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        if "data" in data:
            pages = data["data"]
            print(f"[+] Found {len(pages)} pages:\n")
            for page in pages:
                print(f"    Page: {page['name']}")
                print(f"    ID: {page['id']}")
                print(f"    Token: {page['access_token'][:30]}...")
                print()
            return {p["id"]: p for p in pages}
        else:
            error = data.get("error", {})
            print(f"[!] Failed: {error.get('message', data)}")
            return {}
    except Exception as e:
        print(f"[!] Error: {e}")
        return {}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Facebook Token Manager")
    parser.add_argument("--check", action="store_true", help="Check current token status")
    parser.add_argument("--exchange", action="store_true", help="Exchange for long-lived token")
    parser.add_argument("--page-tokens", action="store_true", help="Get page tokens")
    parser.add_argument("--app-id", type=str, help="Facebook App ID")
    parser.add_argument("--app-secret", type=str, help="Facebook App Secret")
    args = parser.parse_args()

    if args.check:
        check_token()
    elif args.exchange:
        exchange_for_long_lived(args.app_id, args.app_secret)
    elif args.page_tokens:
        get_page_tokens()
    else:
        # Default: check token
        check_token()
