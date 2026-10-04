## Requirements

- A timezone-naive read_at must be treated as UTC instead of raising a validation error.
- Each time this happens must be logged so the firmware issue can be chased.

## Acceptance criteria

- [ ] A naive timestamp is accepted and treated as UTC
- [ ] A warning is logged when a naive timestamp is coerced
- [ ] Regression test with a naive timestamp input

## Out of scope

- Fixing the GW-09 firmware itself (tracked separately with the vendor).
