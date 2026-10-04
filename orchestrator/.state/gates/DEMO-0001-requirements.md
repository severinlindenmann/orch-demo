## Requirements

- A download from a substation gateway may time out transiently.
- Retries must use backoff and give up after a bounded number of attempts.
- Every attempt (success or failure) must be logged with the gateway id.

## Acceptance criteria

- [ ] fetch_with_retry retries up to max_attempts times
- [ ] Backoff is applied between attempts
- [ ] The last exception is re-raised after attempts are exhausted
- [ ] Unit tests cover both the eventual-success and always-fails cases

## Out of scope

- Wiring fetch_with_retry into the nightly job runner itself (follow-up ticket).
