## Requirements

- A single malformed row in a gateway export must not abort the whole file.
- Malformed rows must be logged with enough detail to trace back to the source file.

## Acceptance criteria

- [ ] parse_gateway_export skips a malformed row and logs file name + line number
- [ ] The rest of a file with one bad row among good ones is still ingested
- [ ] Regression test for a file with a mixed good/bad row set

## Out of scope

- Alerting on a sustained rate of malformed rows (separate ticket if it recurs).
