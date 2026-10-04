## Requirements

- CI must report per-module coverage so we can see what's under-tested.
- No behavior change to what passes/fails CI yet, visibility only.

## Acceptance criteria

- [ ] CI runs pytest with --cov=acme --cov-report=term-missing
- [ ] Coverage summary appears in the GitHub Actions log
- [ ] No hard coverage gate introduced in this change

## Out of scope

- Deciding on and enforcing a minimum coverage percentage (needs a follow-up decision).
