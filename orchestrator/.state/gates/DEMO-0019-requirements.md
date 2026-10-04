## Requirements

- Move the gateway download code from acme-energy-data into acme-ingest.
- Run it as its own job defined in acme-infra.
- acme-energy-data only reads the downloaded files.

## Acceptance criteria

- [ ] acme-ingest downloads every gateway with backoff
- [ ] jobs/acme_ingest_service.json exists in acme-infra
- [ ] src/acme/ingest.py no longer downloads anything

## Out of scope

- Changing the export format.

size: l
type: feature
