import os
import random
import string
import requests
import logging

# Logging setup to views logs
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler("otp_events.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

USEPLUNK_API_KEY = os.getenv("USEPLUNK_API_KEY", "")
USEPLUNK_URL = "https://api.useplunk.com/v1/track"

def generate_otp(length=6):
    """Generate a numeric OTP of given length."""
    return ''.join(random.choices(string.digits, k=length))

def send_email_via_useplunk(to_email: str, event: str, data: dict):
    """Send an email event via UsePlunk API."""
    if not USEPLUNK_API_KEY:
        logger.error("UsePlunk API key not found")
        raise ValueError("UsePlunk API key not found")

    headers = {
        "Authorization": f"Bearer {USEPLUNK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"email": to_email, "event": event, "data": data}

    try:
        response = requests.post(USEPLUNK_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"OTP email '{event}' sent to {to_email}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send OTP email '{event}' to {to_email}: {e}")
        return False
