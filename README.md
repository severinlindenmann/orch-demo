# acme-energy-data

> **This is a demo.** Acme Energy is fictional. This repository is the sample workspace for
> [orch-core](https://github.com/severinlindenmann/orch-core): local Markdown tickets with human approvals for agent
> work, plus Mission Control, its dashboard. Tickets live in `orchestrator/`; `AGENTS.md` has the working rules.
>
> - Install the plugin: `claude plugin marketplace add severinlindenmann/orch-core`, then
>   `claude plugin install orch-core@orch-core` (`.claude/settings.json` already names that marketplace).
> - Sub-repos: [orch-demo-ingest](https://github.com/severinlindenmann/orch-demo-ingest),
>   [orch-demo-dbt](https://github.com/severinlindenmann/orch-demo-dbt) and
>   [orch-demo-infra](https://github.com/severinlindenmann/orch-demo-infra), cloned as `ingest/`, `dbt/` and `infra/`:
>   `uv run --project <orch-core>/plugins/orch-core python scripts/seed/seed.py repos --apply`
>   (or `git clone https://github.com/severinlindenmann/orch-demo-ingest ingest`, and the same for `dbt` and `infra`).
> - The demo data (issues, PRs, wiki, tickets) is rebuilt by `scripts/seed/`; see `scripts/seed/README.md`.

Internal data platform for Acme Energy's smart-meter ingestion pipeline.

## What this is

This repository holds the batch jobs that:

1. **Ingest** raw interval-read exports from substation gateways (`src/acme/ingest.py`).
2. **Transform** raw reads into the canonical `meter_reads` fact shape (`src/acme/transform.py`).
3. **Check data quality** before publishing to the warehouse (`src/acme/quality.py`).

Downstream SQL models that build on top of the published tables live in `sql/`.

## Layout

```
src/acme/
  ingest.py       # pull + parse raw gateway exports
  transform.py    # normalize into the meter_reads fact table
  quality.py      # quality gate rules (nulls, range, duplicates)
  config.py       # pipeline configuration
  models.py       # shared dataclasses / pydantic models
  utils.py        # small shared helpers
tests/            # pytest unit tests
sql/staging/      # staging models (1:1 with source tables)
sql/marts/        # curated marts for reporting
```

## Development

```bash
pip install -e .[dev]
pytest -q
```

## Dependency pins

Direct dependencies carry an upper bound (see `pyproject.toml`). Bump the
upper bound deliberately in its own PR, run the full test suite, and only
then widen it, rather than letting a transitive upgrade land unreviewed.

## CI

GitHub Actions runs `pytest -q` against Python 3.11 on every push and pull request (see
`.github/workflows/ci.yml`).
