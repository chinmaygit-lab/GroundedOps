# Integration reliability guide (synthetic example)

Webhooks should include an event identifier and a SHA-256 HMAC signature. Verify the signature before accepting an event, persist its identifier to detect duplicates, and return a successful response for an already accepted event.

Use cursor-based pagination for third-party APIs; save the new cursor only after events from a page are committed. Respect provider rate-limit headers. Use exponential backoff with jitter for temporary failures and stop retrying for invalid authentication.

For a production integration rollout, begin with a pilot tenant, inspect the sync audit log, and confirm that replayed webhooks do not create duplicate tasks. Keep a rollback plan for changes to connector actions.
