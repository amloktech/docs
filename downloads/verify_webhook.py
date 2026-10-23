"""Verify the AMLOK v1.4.2 signature against exact raw request bytes."""
import hashlib
import hmac
import json
import math
import re
import time


def verify_webhook(raw_body, header, secret, now_seconds=None):
    """Return a verified envelope. Caller must persist/deduplicate before 2xx."""
    if not isinstance(raw_body, bytes) or not isinstance(header, str) or not isinstance(secret, str) or not secret:
        raise ValueError("Invalid webhook verification inputs")
    timestamps, signatures = [], []
    for entry in header.split(","):
        pair = entry.strip().split("=")
        if len(pair) != 2:
            raise ValueError("Malformed signature header")
        key, value = pair
        if key == "t":
            timestamps.append(value)
        elif key == "v1":
            signatures.append(value)
    if (len(timestamps) != 1 or not re.fullmatch(r"[0-9]+", timestamps[0]) or
            not signatures or any(not re.fullmatch(r"[a-fA-F0-9]{64}", value) for value in signatures)):
        raise ValueError("Malformed signature header")
    timestamp = int(timestamps[0])
    now = time.time() if now_seconds is None else now_seconds
    if not math.isfinite(now) or abs(now - timestamp) > 300:
        raise ValueError("Webhook timestamp outside the five-minute tolerance")
    signed = timestamps[0].encode("ascii") + b"." + raw_body
    expected = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).digest()
    if not any(hmac.compare_digest(expected, bytes.fromhex(value)) for value in signatures):
        raise ValueError("Invalid webhook signature")
    event = json.loads(raw_body)
    if (not isinstance(event, dict) or not isinstance(event.get("id"), str) or not event["id"] or
            not isinstance(event.get("type"), str) or not isinstance(event.get("resource_id"), str) or
            type(event.get("resource_version")) is not int):
        raise ValueError("Invalid webhook envelope")
    return event
