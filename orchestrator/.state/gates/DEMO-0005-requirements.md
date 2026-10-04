## Requirements

- Direct dependencies (pandas, pydantic) need explicit upper bounds.
- The refresh process for bumping a pin must be documented.

## Acceptance criteria

- [ ] pandas and pydantic carry upper bounds in pyproject.toml
- [ ] README documents how to refresh a pin
- [ ] CI stays green with the new bounds

## Out of scope

- Introducing a full lockfile (uv.lock / poetry.lock) — separate decision.
