/* Reference integration for the documented HubMessage protocol, not an SDK. */
export function mountAmlokHub({ iframe, session, hubOrigin, fetchSession, onState }) {
  const launch = new URL(session.launch_url);
  const trustedOrigin = new URL(hubOrigin).origin;
  if (launch.protocol !== 'https:' || launch.origin !== trustedOrigin) throw new Error('Untrusted Hub URL');
  if (session.embed_origin !== window.location.origin) throw new Error('Session is not bound to this parent');
  if (Date.parse(session.expires_at) <= Date.now()) throw new Error('Expired session');
  const seen = new Set();
  const allowed = new Set(['amlok.hub.ready', 'amlok.hub.completed', 'amlok.hub.cancelled', 'amlok.hub.expired', 'amlok.hub.failed']);
  const listener = async event => {
    if (event.origin !== trustedOrigin || event.source !== iframe.contentWindow) return;
    const message = event.data;
    if (!message || message.protocol_version !== '1' || message.session_id !== session.id ||
        typeof message.event_id !== 'string' || !message.event_id || !allowed.has(message.type)) return;
    if (seen.has(message.event_id)) return;
    seen.add(message.event_id);
    // Bound memory if a faulty frame emits excessive IDs; terminal state is fetched regardless.
    if (seen.size > 256) seen.delete(seen.values().next().value);
    if (message.type === 'amlok.hub.ready') return;
    try {
      // Supplied by your app: calls YOUR authenticated backend, never AMLOK with a browser key.
      const authoritative = await fetchSession(session.id);
      if (authoritative.id !== session.id) throw new Error('Session mismatch');
      onState(authoritative);
    } catch (error) { onState({ id: session.id, status: 'verification_pending', error: error.message }); }
  };
  iframe.title = 'Connect your financial accounts';
  iframe.setAttribute('sandbox', 'allow-scripts allow-forms allow-same-origin allow-popups allow-popups-to-escape-sandbox');
  iframe.referrerPolicy = 'no-referrer';
  window.addEventListener('message', listener);
  iframe.src = launch.href;
  return () => { window.removeEventListener('message', listener); iframe.removeAttribute('src'); };
}
