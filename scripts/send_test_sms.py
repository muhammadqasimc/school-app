import base64
import os
import re
import sys

import requests


def normalize_sa(phone: str) -> str:
    s = str(phone or "").strip()
    s = re.sub(r"[\s\-()]+", "", s)
    if s.startswith("00"):
        s = "+" + s[2:]
    if s.startswith("+"):
        digits = re.sub(r"\D", "", s[1:])
        return "+" + digits
    digits = re.sub(r"\D", "", s)
    if digits.startswith("0") and len(digits) == 10:
        return "+27" + digits[1:]
    if digits.startswith("27") and len(digits) == 11:
        return "+" + digits
    return "+" + digits if digits and not digits.startswith("+") else digits


def mask(phone: str) -> str:
    digits = re.sub(r"\D", "", phone or "")
    if len(digits) <= 4:
        return "*" * max(0, len(digits) - 1) + digits[-1:]
    return "*" * (len(digits) - 4) + digits[-4:]


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: py scripts\\send_test_sms.py <phone> [message]")
        return 2

    client_id = os.environ.get("SMSPORTAL_CLIENT_ID", "").strip()
    api_secret = os.environ.get("SMSPORTAL_API_SECRET", "").strip()
    if not client_id or not api_secret:
        print("Missing SMSPORTAL_CLIENT_ID or SMSPORTAL_API_SECRET env vars.")
        return 2

    sender_id = os.environ.get("SMSPORTAL_SENDER_ID", "").strip() or None
    test_mode = os.environ.get("SMSPORTAL_TEST_MODE", "false").strip().lower() in ("1", "true", "yes", "y")

    to = normalize_sa(sys.argv[1])
    msg = sys.argv[2] if len(sys.argv) >= 3 else "Kismet Parent Portal test SMS (API connectivity check)."

    basic = base64.b64encode(f"{client_id}:{api_secret}".encode("utf-8")).decode("ascii")
    headers = {
        "Authorization": f"Basic {basic}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "sendOptions": {
            "allowContentTrimming": True,
            "testMode": test_mode,
        },
        "messages": [
            {
                "destination": to,
                "content": msg,
                "customerId": "connectivity-test",
            }
        ],
    }
    if sender_id:
        payload["sendOptions"]["senderId"] = sender_id

    resp = requests.post("https://rest.smsportal.com/v3/BulkMessages", headers=headers, json=payload, timeout=20)

    print(f"Destination(masked): {mask(to)}")
    print(f"HTTP: {resp.status_code}")
    try:
        data = resp.json()
        print("Response statusCode:", data.get("statusCode"))
        errors = data.get("errors") or []
        print("Errors:", errors)
        send_resp = (data.get("sendResponse") or {})
        # eventId is useful to confirm provider accepted
        print("EventId:", send_resp.get("eventId"))
        print("Messages enqueued:", send_resp.get("messages"))
        return 0 if resp.status_code == 200 else 1
    except Exception:
        print(resp.text[:2000])
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

