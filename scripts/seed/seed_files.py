"""File trees of the three sub-repos' main branches and their PR branches (demo content, stdlib-only CI)."""
from __future__ import annotations

from dataclasses import dataclass, field

CI_COMMANDS = {
    "ingest": "python -m unittest discover -s tests -t .",
    "dbt": "python ci/lint_sql.py",
    "infra": "python ci/validate.py",
}


def CI_YML(cmd: str) -> str:
    return """name: CI
on:
  push:
    branches: ["**"]
  workflow_dispatch:
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: CMD
""".replace("CMD", cmd)


DEMO_BOT_YML = """name: demo-bot
# Demo only: a second identity (github-actions[bot]) that opens review-requested PRs and posts reviews.
on:
  workflow_dispatch:
    inputs:
      action: {description: "open_pr | approve | request_changes", required: true}
      branch: {description: "head branch for open_pr", required: false, default: ""}
      title: {required: false, default: ""}
      body: {required: false, default: ""}
      reviewer: {required: false, default: ""}
      pr: {description: "PR number for approve and request_changes", required: false, default: ""}
permissions:
  contents: read
  pull-requests: write
jobs:
  act:
    runs-on: ubuntu-latest
    env:
      GH_TOKEN: ${{ github.token }}
      GH_REPO: ${{ github.repository }}
      ACTION: ${{ inputs.action }}
      BRANCH: ${{ inputs.branch }}
      TITLE: ${{ inputs.title }}
      BODY: ${{ inputs.body }}
      REVIEWER: ${{ inputs.reviewer }}
      PR: ${{ inputs.pr }}
    steps:
      - run: |
          case "$ACTION" in
            open_pr) gh pr create --head "$BRANCH" --base main --title "$TITLE" --body "$BODY" --reviewer "$REVIEWER" ;;
            approve) gh pr review "$PR" --approve --body "$BODY" ;;
            request_changes) gh pr review "$PR" --request-changes --body "$BODY" ;;
            *) echo "unknown action: $ACTION"; exit 1 ;;
          esac
"""

_DOWNLOAD = '''"""Download gateway exports with retry and backoff."""


def backoff_seconds(attempt: int, retry_after: int | None = None) -> int | None:
    """Seconds to wait before retry `attempt` (1-based); None means give up."""
    if attempt > 5:
        return None
    if retry_after is not None:
        return retry_after
    return min(2 ** attempt, 60)


def parse_export(text: str) -> list[dict]:
    header, *rows = text.splitlines()
    names = header.split(",")
    return [dict(zip(names, row.split(","))) for row in rows if row]
'''

_TEST_DOWNLOAD = '''import sys
import unittest

sys.path.insert(0, "src")
from acme_ingest.download import backoff_seconds, parse_export  # noqa: E402


class Backoff(unittest.TestCase):
    def test_grows_and_gives_up(self):
        self.assertEqual([backoff_seconds(a) for a in (1, 2, 6)], [2, 4, None])

    def test_retry_after_wins(self):
        self.assertEqual(backoff_seconds(1, retry_after=9), 9)


class Parse(unittest.TestCase):
    def test_rows(self):
        self.assertEqual(parse_export("meter,kwh\\nm1,3\\n"), [{"meter": "m1", "kwh": "3"}])
'''

_LINT = '''"""Demo SQL lint: every model starts with a '-- grain:' line and never uses select *."""
import pathlib
import re
import sys

bad = []
for p in sorted(pathlib.Path("models").rglob("*.sql")):
    text = p.read_text()
    if not text.startswith("-- grain:"):
        bad.append(f"{p}: the first line must be '-- grain: ...'")
    if re.search(r"select\\s+\\*", text, re.IGNORECASE):
        bad.append(f"{p}: select * is not allowed")
print("\\n".join(bad) or "ok")
sys.exit(1 if bad else 0)
'''

_VALIDATE = '''"""Demo infra check: every JSON file parses and every job carries tags.cost_center."""
import json
import pathlib
import sys

bad = []
for p in sorted(pathlib.Path(".").glob("*/*.json")):
    try:
        data = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        bad.append(f"{p}: {e}")
        continue
    if p.parts[0] == "jobs" and not (data.get("tags") or {}).get("cost_center"):
        bad.append(f"{p}: tags.cost_center is required")
print("\\n".join(bad) or "ok")
sys.exit(1 if bad else 0)
'''

FCT_MAIN = """-- grain: one row per meter and interval
select r.meter_id, r.read_at, r.kwh, m.meter_type
from {{ ref('stg_meter_reads') }} r
join {{ ref('stg_meters') }} m using (meter_id)
where r.kwh >= 0
"""

STG_METERS_MAIN = """-- grain: one row per meter
select meter_id, meterType as meter_type, installed_on
from {{ source('raw', 'meters') }}
"""

_DEMO_NOTE = "Demo repository for orch Mission Control (Acme Energy is fictional). Not production code."


def _common(name: str) -> dict[str, str]:
    return {".github/workflows/ci.yml": CI_YML(CI_COMMANDS[name]), ".github/workflows/demo-bot.yml": DEMO_BOT_YML}


MAIN_TREES: dict[str, dict[str, str]] = {
    "ingest": {
        **_common("ingest"),
        "README.md": f"# acme-ingest\n\nGateway download service for Acme Energy.\n\n{_DEMO_NOTE}\n\n"
                     f"Checks: `{CI_COMMANDS['ingest']}`\n",
        "src/acme_ingest/__init__.py": "",
        "src/acme_ingest/download.py": _DOWNLOAD,
        "config/gateways.json": '{"gateways": ["gw-01", "gw-07"], "timeout_s": 30}\n',
        "tests/__init__.py": "",
        "tests/test_download.py": _TEST_DOWNLOAD,
    },
    "dbt": {
        **_common("dbt"),
        "README.md": f"# acme-dbt\n\ndbt models for Acme Energy's meter marts.\n\n{_DEMO_NOTE}\n\n"
                     f"Checks: `{CI_COMMANDS['dbt']}`\n",
        "dbt_project.yml": "name: acme_dbt\nversion: '1.0.0'\nprofile: acme\nmodel-paths: ['models']\nmacro-paths: ['macros']\n",
        "models/staging/stg_meter_reads.sql": "-- grain: one row per meter and interval\n"
                                              "select meter_id, read_at, kwh\nfrom {{ source('raw', 'meter_reads') }}\n",
        "models/staging/stg_meters.sql": STG_METERS_MAIN,
        "models/marts/fct_meter_reads.sql": FCT_MAIN,
        "ci/lint_sql.py": _LINT,
    },
    "infra": {
        **_common("infra"),
        "README.md": f"# acme-infra\n\nEnvironment and job definitions (JSON) for Acme Energy.\n\n{_DEMO_NOTE}\n\n"
                     "Nothing here is deployed: the demo never runs `databricks bundle` commands.\n\n"
                     f"Checks: `{CI_COMMANDS['infra']}`\n",
        "envs/dev.json": '{"name": "dev", "serverless": false}\n',
        "envs/int.json": '{"name": "int", "host": "https://adb-1111111111111111.11.azuredatabricks.net"}\n',
        "envs/prod.json": '{"name": "prod", "host": "https://adb-2222222222222222.12.azuredatabricks.net"}\n',
        "jobs/acme_ingest_daily.json": '{"name": "acme-ingest-daily", "schedule": "0 30 5 * * ?", '
                                       '"tags": {"cost_center": "data-platform"}}\n',
        "ci/validate.py": _VALIDATE,
    },
}


# The enterprise policy forbids GitHub Actions to create or approve PRs, and GitHub never lets an author review or
# request a review from themselves. With one account these planned states cannot be seeded: such a PR is opened
# without any review ("open") and the checklist reports the planned state as an allowed finding.
NEEDS_SECOND_ACCOUNT = frozenset({"review_requested", "approved", "changes_requested"})
SECOND_ACCOUNT_HINT = "needs a second GitHub account or an enterprise admin to allow Actions to approve PRs"


@dataclass(frozen=True)
class PrSpec:
    repo: str
    branch: str
    title: str
    state: str  # the planned state; seeded_state is what one gh account can really produce
    files: dict = field(default_factory=dict)
    ticket: str | None = None
    main_commit: dict | None = None

    @property
    def seeded_state(self) -> str:
        return "open" if self.state in NEEDS_SECOND_ACCOUNT else self.state

    @property
    def body(self) -> str:
        summary = self.title.removeprefix("Draft: ")
        summary = summary.split(" ", 1)[1] if self.ticket else summary
        shown = "open, no review yet" if self.seeded_state == "open" else self.seeded_state
        return (f"What: {summary}.\nWhy: Demo PR in the '{shown}' state for Mission Control's Code reviews page.\n"
                f"Risk: None; demo repository.\nVerification: CI (`{CI_COMMANDS[self.repo]}`).")


_DOWNLOAD_EMPTY = _DOWNLOAD.replace(
    '    header, *rows = text.splitlines()',
    '    if not text.strip():\n        return []\n    header, *rows = text.splitlines()')
_TEST_EMPTY = _TEST_DOWNLOAD + '''
    def test_empty_export(self):
        self.assertEqual(parse_export(""), [])
'''
_TEST_429 = _TEST_DOWNLOAD + '''

class TooManyRequests(unittest.TestCase):
    def test_429_without_retry_after_waits_30s(self):
        self.assertEqual(backoff_seconds(1, retry_after=None, status=429), 30)
'''

PR_SPECS: tuple[PrSpec, ...] = (
    # ingest
    PrSpec("ingest", "fix/DEMO-0020-handle-429", "DEMO-0020 Back off 30 s on HTTP 429 without Retry-After", "failing",
           {"tests/test_download.py": _TEST_429}, ticket="DEMO-0020"),
    PrSpec("ingest", "feature/DEMO-0019-gateway-client", "DEMO-0019 Move the gateway client into acme-ingest",
           "review_requested",
           {"src/acme_ingest/client.py": '"""Gateway client moved here from acme-energy-data (DEMO-0019)."""\n'
                                         "from acme_ingest.download import backoff_seconds\n\n\n"
                                         "def plan_retries(max_attempts: int = 5) -> list[int]:\n"
                                         "    return [s for a in range(1, max_attempts + 1) if (s := backoff_seconds(a)) is not None]\n",
            "tests/test_client.py": 'import sys\nimport unittest\n\nsys.path.insert(0, "src")\n'
                                    "from acme_ingest.client import plan_retries  # noqa: E402\n\n\n"
                                    "class Client(unittest.TestCase):\n    def test_plan(self):\n"
                                    "        self.assertEqual(plan_retries(3), [2, 4, 8])\n"},
           ticket="DEMO-0019"),
    PrSpec("ingest", "wip/structured-logging", "Draft: Add structured logging helpers", "draft",
           {"src/acme_ingest/log.py": '"""Structured log events (WIP)."""\n\n\n'
                                      "def event(name: str, **fields) -> dict:\n    return {\"event\": name, **fields}\n"}),
    PrSpec("ingest", "fix/DEMO-0027-empty-export", "DEMO-0027 Return no rows for an empty gateway export", "approved",
           {"src/acme_ingest/download.py": _DOWNLOAD_EMPTY, "tests/test_download.py": _TEST_EMPTY}, ticket="DEMO-0027"),
    PrSpec("ingest", "chore/raise-download-timeout", "Raise the gateway download timeout to 60 s", "conflict",
           {"config/gateways.json": '{"gateways": ["gw-01", "gw-07"], "timeout_s": 60}\n'},
           main_commit={"subject": "Lower the gateway download timeout to 20 s",
                        "files": {"config/gateways.json": '{"gateways": ["gw-01", "gw-07"], "timeout_s": 20}\n'}}),
    # dbt
    PrSpec("dbt", "feature/DEMO-0021-meter-type-dim", "DEMO-0021 Add the dim_meter_type model", "failing",
           {"models/marts/dim_meter_type.sql": "-- grain: one row per meter type\nselect *\nfrom {{ ref('stg_meters') }}\n"},
           ticket="DEMO-0021"),
    PrSpec("dbt", "chore/source-freshness", "Add source freshness checks", "review_requested",
           {"models/staging/sources.yml": "version: 2\nsources:\n  - name: raw\n    freshness:\n"
                                          "      warn_after: {count: 6, period: hour}\n    loaded_at_field: _loaded_at\n"
                                          "    tables:\n      - name: meter_reads\n      - name: meters\n"}),
    PrSpec("dbt", "explore/dbt-utils-macros", "Draft: Try a cents_to_chf macro", "draft",
           {"macros/cents_to_chf.sql": "{% macro cents_to_chf(column) %}({{ column }} / 100.0){% endmacro %}\n"}),
    PrSpec("dbt", "chore/snake-case-columns", "Read meters_v2 with snake_case columns", "approved",
           {"models/staging/stg_meters.sql": "-- grain: one row per meter\nselect meter_id, meter_type, installed_on\n"
                                             "from {{ source('raw', 'meters_v2') }}\n"}),
    PrSpec("dbt", "feature/DEMO-0028-dst-days", "DEMO-0028 Skip reads without a timestamp on DST days", "conflict",
           {"models/marts/fct_meter_reads.sql": FCT_MAIN.replace("where r.kwh >= 0", "where r.kwh >= 0 and r.read_at is not null")},
           ticket="DEMO-0028",
           main_commit={"subject": "Drop zero reads from fct_meter_reads",
                        "files": {"models/marts/fct_meter_reads.sql": FCT_MAIN.replace("where r.kwh >= 0", "where r.kwh > 0")}}),
    PrSpec("dbt", "feature/DEMO-0026-incremental-reads", "DEMO-0026 Add an incremental fct_meter_reads", "changes_requested",
           {"models/marts/fct_meter_reads_incremental.sql":
                "-- grain: one row per meter and interval\n"
                "{{ config(materialized='incremental', unique_key=['meter_id', 'read_at']) }}\n"
                "select meter_id, read_at, kwh\nfrom {{ ref('stg_meter_reads') }}\n"
                "{% if is_incremental() %}\nwhere read_at > (select max(read_at) from {{ this }})\n{% endif %}\n"},
           ticket="DEMO-0026"),
    # infra
    PrSpec("infra", "chore/DEMO-0025-cost-center-tags", "DEMO-0025 Add the dbt build job", "failing",
           {"jobs/acme_dbt_build.json": '{"name": "acme-dbt-build", "schedule": "0 0 6 * * ?", "tags": {"team": "data"}}\n'},
           ticket="DEMO-0025"),
    PrSpec("infra", "chore/default-tags", "Add the quality checks job with default tags", "review_requested",
           {"jobs/acme_quality_checks.json": '{"name": "acme-quality-checks", "schedule": "0 0 7 * * ?", '
                                             '"tags": {"cost_center": "data-platform"}}\n'}),
    PrSpec("infra", "feature/DEMO-0019-ingest-service-job", "Draft: DEMO-0019 Add the ingest service job", "draft",
           {"jobs/acme_ingest_service.json": '{"name": "acme-ingest-service", "schedule": "0 */15 * * * ?", '
                                             '"tags": {"cost_center": "data-platform"}}\n'},
           ticket="DEMO-0019"),
    PrSpec("infra", "chore/serverless-defaults", "Use serverless compute in dev", "approved",
           {"envs/dev.json": '{"name": "dev", "serverless": true}\n'}),
    PrSpec("infra", "chore/rename-int-workspace", "Point int at the 3333 workspace", "conflict",
           {"envs/int.json": '{"name": "int", "host": "https://adb-3333333333333333.13.azuredatabricks.net"}\n'},
           main_commit={"subject": "Point int at the new workspace host",
                        "files": {"envs/int.json": '{"name": "int", "host": "https://adb-4444444444444444.14.azuredatabricks.net"}\n'}}),
)
