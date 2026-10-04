## Requirements

- Gateway exports that fail transiently are retried, not lost.
- Corrupt exports are rejected before they reach staging.
- Ops hear about a gateway that keeps failing.

## Acceptance criteria

- [ ] Every child is done or explicitly dropped
- [ ] No export lost in a week of int runs

## Out of scope



size: l
type: epic
