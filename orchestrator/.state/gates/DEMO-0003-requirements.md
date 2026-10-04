## Requirements

- The on-call summary line must never raise ZeroDivisionError on an empty run.
- An empty run (no reads at all) must report a clean zero suspect rate.

## Acceptance criteria

- [ ] suspect_rate_percent() handles total_rows == 0 without raising
- [ ] Regression test for the empty-report case
- [ ] Normal non-empty case still computes the correct percentage

## Out of scope

- Reworking QualityReport's public API beyond this one summary helper.
