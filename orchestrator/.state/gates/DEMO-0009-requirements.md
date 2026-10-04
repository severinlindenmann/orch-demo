## Requirements

- A gateway export older than allowed_late_days must be rejected with a clear error.
- A late-but-allowed export must be accepted and logged as late.

## Acceptance criteria

- [ ] check_export_age() returns False for on-time, True for late-but-allowed
- [ ] check_export_age() raises ExportTooLateError beyond allowed_late_days
- [ ] Tests cover on-time, late-but-allowed and rejected cases

## Out of scope

- Wiring the check into the nightly runner's main loop (follow-up ticket).
