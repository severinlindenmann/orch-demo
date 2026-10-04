## Requirements

- Duplicate (meter_id, read_at) rows above zero must fail the quality gate by default.
- The failure message must include the duplicate count and an example key.

## Acceptance criteria

- [ ] QualityReport.passed() fails when duplicate_rows > 0
- [ ] Failure message includes count and an example (meter_id, read_at)
- [ ] Existing passing-run tests still pass unchanged

## Out of scope

- Automatic de-duplication at ingest time (handled separately by dedupe_reads).
