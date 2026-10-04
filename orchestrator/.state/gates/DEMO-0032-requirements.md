## Requirements

- Retry a download that answers HTTP 503 up to three times with backoff.

## Acceptance criteria

- [ ] A 503 then 200 sequence loads the file
- [ ] Three 503s in a row fail the run with the URL

## Out of scope



size: s
type: feature
