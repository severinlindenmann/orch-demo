## Plan

1. Add fetch_with_retry(download_fn, gateway_id, max_attempts) to acme.ingest.
2. Linear backoff (0.5s * attempt) between retries; log each failed attempt.
3. Re-raise the last exception once attempts are exhausted.
4. Unit tests with a fake flaky callable (fails N times then succeeds; always fails).
