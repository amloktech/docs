## Signature contract

```text
X-AMLOK-Signature: t=<unix_seconds>,v1=<hex_hmac>
signed_bytes = UTF8(timestamp + ".") + exact_raw_request_body
hex_hmac = HMAC-SHA256(webhook_secret, signed_bytes)
```

Verify the exact bytes before JSON parsing or reserialization. Compare the digest in constant time. The timestamp tolerance is five minutes in either direction; keep the receiver's clock synchronized.

The following helpers implement the signature format. They validate the signature and basic envelope, but your application must still enforce destination/tenant association, durable deduplication, payload validation, and processing rules.

<Tabs>
<Tab title="Node.js">

```javascript
import { createHmac, timingSafeEqual } from 'node:crypto';

// AMLOK signature contract. Does not acknowledge or deduplicate.
// rawBody must be the exact received bytes, before JSON parsing or reserialization.
export function verifyWebhook(rawBody, header, secret, nowSeconds = Math.floor(Date.now() / 1000)) {
  if (!Buffer.isBuffer(rawBody) || typeof header !== 'string' || typeof secret !== 'string' || !secret) {
    throw new Error('Invalid webhook verification inputs');
  }
  const timestamps = [];
  const signatures = [];
  for (const entry of header.split(',')) {
    const pair = entry.trim().split('=');
    if (pair.length !== 2) throw new Error('Malformed signature header');
    const [key, value] = pair;
    if (key === 't') timestamps.push(value);
    else if (key === 'v1') signatures.push(value);
  }
  if (timestamps.length !== 1 || !/^\d+$/.test(timestamps[0]) || signatures.length === 0 ||
      signatures.some(value => !/^[a-fA-F0-9]{64}$/.test(value))) {
    throw new Error('Malformed signature header');
  }
  const timestamp = Number(timestamps[0]);
  if (!Number.isSafeInteger(timestamp) || !Number.isFinite(nowSeconds) || Math.abs(nowSeconds - timestamp) > 300) {
    throw new Error('Webhook timestamp outside the five-minute tolerance');
  }
  const expected = createHmac('sha256', secret)
    .update(timestamps[0] + '.', 'utf8').update(rawBody).digest();
  const verified = signatures.some(value => timingSafeEqual(expected, Buffer.from(value, 'hex')));
  if (!verified) throw new Error('Invalid webhook signature');
  const event = JSON.parse(rawBody.toString('utf8'));
  if (!event || typeof event !== 'object' || Array.isArray(event) ||
      typeof event.id !== 'string' || !event.id || typeof event.type !== 'string' ||
      typeof event.resource_id !== 'string' || !Number.isInteger(event.resource_version)) {
    throw new Error('Invalid webhook envelope');
  }
  return event;
}

```

</Tab>
<Tab title="Python">

```python
"""Verify the AMLOK signature against exact raw request bytes."""
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

```

</Tab>
</Tabs>

## Receive, persist, acknowledge

1. Apply a configured body-size limit and capture the raw bytes. Use the payload limit configured for your environment.
2. Resolve the expected secret from the registered destination, not from an untrusted body field.
3. Verify the signature and timestamp, then validate the event against the contract.
4. Atomically insert the event into a durable inbox with a unique key of workspace/environment + event ID. Persist its processing job in the same transaction, or use a transactional outbox.
5. Return `2xx` after durable acceptance. A duplicate already accepted event can receive `2xx` without repeating its effects.
6. Process asynchronously. Fetch the authorized resource and apply only a newer resource version.

Do not mark an event complete before its effects are durably committed. A worker failure after acknowledgment must be recoverable from your inbox; the sender may not deliver again. An invalid signature should receive a non-2xx response and must not enter the business-processing queue.

## Delivery, retries, and replay

Delivery is at least once, and arrival order is not guaranteed. Keep deduplication records for the agreed replay window, not merely the five-minute signature tolerance.

There is one initial attempt and at most six automatic retries. Delays after each successive failed attempt are **1 minute, 5 minutes, 30 minutes, 2 hours, 8 hours, and 24 hours** (seven attempts total). These are successive delays, not offsets from the first attempt. Any non-2xx response, including 3xx and 4xx, is unsuccessful. Redirects are never followed; Retry-After from the receiver does not replace this schedule. Unsafe destinations, disabled/unsubscribed endpoints and oversized payloads stop automatic delivery. Terminal failures require [delivery review and reconciliation](/api-reference/webhook-operations). List retained events to discover missing IDs and delivery attempts to inspect failures.

[Replay](/api-reference/endpoints/events/replay-event) preserves the original event ID. It must use a fresh delivery timestamp/signature so delayed replay can pass timestamp verification. The timeout is 10 seconds including DNS, connection and TLS, the body limit is 64 KiB, the signing-secret overlap is 24 hours and event replay retention is 30 days. The endpoint drawer shows these settings. Authorized administrators manage URLs, subscriptions, enablement and secret rotation in the client portal; follow the [webhook operations procedure](/api-reference/webhook-operations).

Event bodies contain resource references and limited status changes. Retrieve sensitive evidence through authenticated API reads. Do not add provider credentials, identity media, or unrestricted raw payloads to event logs.


## Destination requirements

Register a public DNS hostname using HTTPS on port 443. Paths and query parameters are supported; do not place credentials in them. URL usernames, passwords, fragments, IP literals and private/local destinations are rejected. DNS is checked on every attempt and the validated public address is pinned for that connection. All resolved addresses must be public, including IPv6. Your TLS certificate must match the hostname and chain to a trusted authority.

The endpoint is scoped to one workspace and Sandbox or Live environment. Use distinct destinations and signing secrets for each. Your receiver must accept POST with application/json; no browser cookie, CSRF token, Basic authentication, custom Bearer header or mutual TLS is sent. Authenticate with X-AMLOK-Signature. Keep your AMLOK API key on your server for resource reads; never use it as the webhook signing secret. Do not use source IP as the sole authentication check.

## Rotate a signing secret

Open the endpoint drawer and choose **Rotate signing secret**, then confirm your identity. Save the new secret shown once. For 24 hours, each attempt carries both the new and previous signatures as separate `v1` values; the timestamp and raw body are identical. Update your receiver to the new secret during the overlap. The helpers above accept any matching `v1` signature. After expiry only the new secret signs attempts, including replays. Another rotation during the overlap is rejected to avoid unexpectedly invalidating the previous secret.

If a secret is compromised, disable the endpoint immediately, replace the destination/secret and verify your receiver before re-enabling. Rotation overlap is for continuity, not immediate revocation; do not depend on it to revoke a stolen secret.
