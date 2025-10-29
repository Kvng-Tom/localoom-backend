import os
import re
import random
import string
import requests
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)

# -------------------- Normalizers --------------------
def normalize_phone_number(value: str) -> str:
    """Normalize Nigerian numbers to +234 format."""
    if not value:
        return value

    value = str(value).strip().replace(" ", "")
    if value.startswith("0"):
        value = "+234" + value[1:]
    elif value.startswith("234"):
        value = "+" + value

    pattern = r'^\+234\d{10}$'
    if not re.match(pattern, value):
        raise ValidationError("Enter a valid Nigerian phone number (e.g. 08012345678).")

    return value


# -------------------- OTP --------------------
def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))


# -------------------- Email (UsePlunk) --------------------
USEPLUNK_API_KEY = os.getenv("USEPLUNK_API_KEY", "")
USEPLUNK_URL = "https://api.useplunk.com/v1/track"

def send_email_via_useplunk(to_email: str, event: str, data: dict):
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


# -------------------- SMS (Termii) --------------------
TERMII_BASE = getattr(settings, "TERMII_BASE_URL", "https://api.ng.termii.com")

def send_sms_via_termii(phone_number: str, otp_code: str) -> bool:
    if not settings.TERMII_API_KEY:
        logger.warning("TERMII_API_KEY not set; skipping SMS send.")
        return False

    url = f"{TERMII_BASE.rstrip('/')}/api/sms/send"
    payload = {
        "to": phone_number,
        "from": "LocalLoom",
        "sms": f"Your LocalLoom verification code is {otp_code}. It expires in 10 minutes.",
        "type": "plain",
        "channel": "generic",
        "api_key": settings.TERMII_API_KEY,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Termii SMS response: %s", resp.json())
        return True
    except requests.RequestException as exc:
        logger.error("Termii SMS failed: %s", exc)
        return False


# -------------------- User Helpers --------------------
def get_user_by_identifier(identifier: str):
    """Return user by email or phone_number."""
    User = get_user_model()
    try:
        if "@" in identifier:  # email case
            return User.objects.get(email=identifier)
        # phone_number case: normalize to +234 format
        normalized = normalize_phone_number(identifier)
        return User.objects.get(phone_number=normalized)
    except User.DoesNotExist:
        return None


def send_user_otp(user, otp_code, purpose="signup"):
    """
    Send OTP to user:
    - Prefer email if email exists.
    - Otherwise use phone number.
    """
    results = {"email": False, "sms": False}

    if user.email:
        try:
            results["email"] = send_email_via_useplunk(
                to_email=user.email,
                event=purpose,
                data={"full_name": user.full_name, "otp": str(otp_code)},
            )
        except Exception as exc:
            logger.error("Failed to send OTP email to %s: %s", user.email, exc)

    elif user.phone_number:
        try:
            results["sms"] = send_sms_via_termii(user.phone_number, otp_code)
        except Exception as exc:
            logger.error("Failed to send OTP SMS to %s: %s", user.phone_number, exc)

    return results

# -------------------- Custom Exception Handler --------------------
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # Simplify field error messages
        for field, errors in response.data.items():
            if isinstance(errors, list):
                response.data[field] = " ".join(errors)

    # Handle specific exceptions
    if response is None:
        return requests.Response({"error": "Something went wrong. Please try again."}, status=500)

    return response
