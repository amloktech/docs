import { createHmac, timingSafeEqual } from 'node:crypto';

// Proposed AMLOK v0.1.0 signature contract. Does not acknowledge or deduplicate.
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
    throw new Error('Webhook timestamp outside the proposed five-minute tolerance');
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
