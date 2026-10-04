## Requirements

- Gateway exports in DD/MM/YYYY HH:MM must be accepted alongside ISO 8601.
- The alternate format must be normalized before pydantic validation.

## Acceptance criteria

- [ ] _parse_timestamp accepts both ISO 8601 and DD/MM/YYYY HH:MM
- [ ] A file using the alternate format parses successfully end to end
- [ ] Every other gateway's ISO 8601 timestamps are unaffected

## Out of scope

- Auto-detecting and supporting further timestamp formats beyond these two.
