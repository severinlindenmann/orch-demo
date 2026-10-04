"""The new demo tickets as recipes of real orch operations. Keys are fixed: commits, PRs and wiki pages cite
DEMO-0016..0030; DEMO-0031..0036 are the epic and delegation examples.

A recipe's steps run at `at` on the timeline; a step ("at", x) starts a later batch of the same ticket at x (an
epic's children are written before the epic approval and worked after it). A `late` ticket is created by its agent
when its first batch runs, not in the creation phase: a child added after its epic's approval (late tickets are the
highest keys, created in key order)."""
from __future__ import annotations

from dataclasses import dataclass

UNITTEST = "python -m unittest discover -s tests -t ."


@dataclass(frozen=True)
class TicketSpec:
    key: str
    title: str
    type: str
    priority: str
    size: str
    harness: str
    issue: str | None
    at: float                 # 0..1: where on the timeline the steps run (creation happens first, in key order)
    steps: tuple
    from_key: str | None = None
    ask: str = ""
    epic: str | None = None   # created as a child of this epic
    late: bool = False


def R(reqs, acs, oos=None) -> dict:
    out = {"Requirements": "\n".join(f"- {r}" for r in reqs),
           "Acceptance criteria": "\n".join(f"- [ ] {a}" for a in acs)}
    if oos:
        out["Out of scope"] = f"- {oos}"
    return out


def Q(text, why, options, rec, blocking=True) -> dict:
    return {"text": text, "why": why, "type": "single", "recommended": rec, "blocking": blocking,
            "options": [{"key": k, "label": label, "cost": cost} for k, label, cost in options]}


TICKETS: tuple[TicketSpec, ...] = (
    TicketSpec("DEMO-0016", "Investigate failed acme-ingest-daily runs on int", "investigation", "normal", "m",
               "claude-code", "i16", 0.10, (
        ("sections", {"Context": "Run 9001 of acme-ingest-daily failed on int (Databricks page, int · simulated). "
                                 "prod ran fine on the same day.",
                      **R(["Find the root cause of int run 9001.", "Say whether prod is exposed to the same failure."],
                          ["Root cause written to Findings with the evidence", "A decision: fix now or file a follow-up"])}),
        ("ask", [Q("Alert on the first failed run or only after two in a row?",
                   "Decides whether the fix also changes the alert rule.",
                   [("A", "Alert on the first failure", "more noise at night"),
                    ("B", "Alert after two failures in a row", "one day later on real outages")], "B", blocking=False)]),
    )),
    TicketSpec("DEMO-0017", "Load tariff tables as dbt seeds", "feature", "high", "m", "claude-code", "i17", 0.05, (
        ("sections", R(["Load the tariff tables as dbt seeds.", "Tariffs join to fct_meter_reads by tariff_code."],
                       ["seeds/tariffs.csv loads with dbt seed", "fct_meter_reads carries tariff_code"])),
        ("changes", "requirements", "Say which tariff years are in scope and who owns the CSV, then ask me again."),
    )),
    TicketSpec("DEMO-0018", "Rename the staging schema to stg_acme", "chore", "low", "s", "claude-code", "i18", 0.15, (
        ("sections", R(["Rename the staging schema from staging to stg_acme."],
                       ["All staging models build into stg_acme", "No mart references the old schema"])),
        ("approve", "requirements"),
        ("edit", "Requirements", "- Rename the staging schema from staging to stg_acme.\n"
                                 "- Keep a view in the old schema for one sprint so dashboards keep working."),
    )),
    TicketSpec("DEMO-0019", "Move the gateway download into the ingest service", "feature", "normal", "l", "copilot",
               "i19", 0.85, (
        ("sections", R(["Move the gateway download code from acme-energy-data into acme-ingest.",
                        "Run it as its own job defined in acme-infra.",
                        "acme-energy-data only reads the downloaded files."],
                       ["acme-ingest downloads every gateway with backoff",
                        "jobs/acme_ingest_service.json exists in acme-infra",
                        "src/acme/ingest.py no longer downloads anything"], oos="Changing the export format.")),
        ("approve", "requirements"),
        ("claim",),
        ("sections", {"Plan": "1. Copy the client into acme-ingest with tests.\n2. Add the job definition in acme-infra.\n"
                              "3. Remove the old download code here.\n4. Merge order: ingest, then infra, then acme-energy-data."}),
        ("tasks", [{"text": "Copy the download client into acme-ingest", "refs": ["file:ingest/src/acme_ingest/download.py"],
                    "verify": UNITTEST},
                   {"text": "Add the ingest service job to acme-infra", "refs": ["file:infra/jobs/acme_ingest_daily.json"],
                    "needs": ["T1"]},
                   {"text": "Remove the old download code from acme-energy-data", "refs": ["file:src/acme/ingest.py"],
                    "needs": ["T1", "T2"]},
                   {"text": "Approve the service principal for the new job", "owner": "human"}]),
        ("approve", "plan"),
        ("start", "T1"),
        ("done", "T1", "unit tests green on feature/DEMO-0019-gateway-client"),
        ("start", "T2"),
        ("link", "ingest", "feature/DEMO-0019-gateway-client", True),
        ("link", "infra", "feature/DEMO-0019-ingest-service-job", True),
        ("link", "acme-energy-data", "feature/DEMO-0019-remove-old-download", False),
        ("state", "T1 is done; its ingest PR waits for your review. T2 is a draft PR in acme-infra. T3 starts after both merge."),
    )),
    TicketSpec("DEMO-0020", "Downloader crashes on HTTP 429 without Retry-After", "bug", "urgent", "s", "claude-code",
               "i20", 0.90, (
        ("sections", {"Context": "acme-ingest crashes when a gateway answers 429 without Retry-After (seen on gw-07).",
                      **R(["Back off 30 s on HTTP 429 when Retry-After is missing."],
                          ["A test reproduces the crash", "The downloader waits 30 s and retries"])}),
        ("approve", "requirements"),
        ("claim",),
        ("sections", {"Plan": "Reproduce with a test first, then back off 30 s when Retry-After is missing."}),
        ("tasks", [{"text": "Reproduce the crash with a 429 test", "refs": ["file:ingest/tests/test_download.py"]},
                   {"text": "Back off 30 s when Retry-After is missing", "refs": ["file:ingest/src/acme_ingest/download.py"],
                    "verify": UNITTEST}]),
        ("approve", "plan"),
        ("start", "T1"),
        ("done", "T1", "test_429_without_retry_after_waits_30s reproduces it"),
        ("start", "T2"),
        ("link", "ingest", "fix/DEMO-0020-handle-429", True),
        ("artifact", {"name": "429-repro.log", "kind": "log", "label": "Unit tests after the 429 fix", "task": "T1", "ac": 1}),
        ("artifact_link", {"repo": "ingest", "branch": "fix/DEMO-0020-handle-429", "suffix": "/checks",
                           "kind": "build", "label": "CI run on the fix PR", "task": "T2", "ac": 2}),
        ("log", "CI fails on purpose for now: the reproducing test landed before the fix."),
    )),
    TicketSpec("DEMO-0021", "Add a meter_type dimension to the dbt marts", "feature", "normal", "m", "claude-code",
               "i21", 0.80, (
        ("sections", R(["Add dim_meter_type and join it in fct_meter_reads."],
                       ["dim_meter_type builds", "fct_meter_reads joins it", "The SQL lint stays green"])),
        ("approve", "requirements"),
        ("claim",),
        ("sections", {"Plan": "1. Write dim_meter_type.\n2. Join it in fct_meter_reads.\n3. Drop meter_type from stg_meters."}),
        ("tasks", [{"text": "Write dim_meter_type", "refs": ["file:dbt/models/marts/fct_meter_reads.sql"]},
                   {"text": "Join dim_meter_type in fct_meter_reads", "needs": ["T1"]},
                   {"text": "Drop meter_type from stg_meters"}]),
        ("approve", "plan"),
        ("start", "T1"),
        ("skip", "T3", "stg_meters keeps meter_type until DEMO-0023 ships"),
        ("link", "dbt", "feature/DEMO-0021-meter-type-dim", True),
        ("log", "The SQL lint fails: dim_meter_type still uses select *."),
    )),
    TicketSpec("DEMO-0022", "Use meter_type in the suspect-threshold mart", "feature", "normal", "m", "claude-code",
               "i22", 0.20, (
        ("sections", R(["Pick the suspect threshold per meter type from dim_meter_type."],
                       ["Each meter type has its own threshold", "The mart builds in under 5 min"])),
        ("approve", "requirements"),
        ("raw", {"blocked_by": ["DEMO-0021"]}),
    )),
    TicketSpec("DEMO-0023", "Show suspect thresholds in the daily report", "feature", "normal", "s", "copilot",
               "i23", 0.25, (
        ("sections", R(["Show the threshold that applied next to each suspect read in the daily report.",
                        "Layout as in the mock-up:\n\n"
                        "  ![Daily report with a threshold column](artifact:daily-report-mockup.png)\n"],
                       ["The report has a threshold column", "Old reports still render"])),
        ("artifact", {"name": "daily-report-mockup.png", "kind": "screenshot",
                      "label": "Daily report mock-up with the threshold column", "ac": 1}),
        ("approve", "requirements"),
        ("raw", {"blocked_by": ["DEMO-0022"]}),
    )),
    TicketSpec("DEMO-0024", "Add the int workspace to the deploy targets", "feature", "normal", "m", "claude-code",
               "i24", 0.70, (
        ("sections", R(["Add an int target next to dev and prod."], ["envs/int.json is validated by CI", "Runbook updated"])),
        ("approve", "requirements"),
        ("claim",),
        ("sections", {"Plan": "Add int to envs/ and share defaults with prod through a common file."}),
        ("changes", "plan", "Keep int and prod in separate files with no shared defaults, then ask me again."),
    )),
    TicketSpec("DEMO-0025", "Tag every job with cost_center", "chore", "normal", "s", "copilot", "i25", 0.0, (
        ("sections", R(["Every job file carries tags.cost_center.", "CI refuses a job without it."],
                       ["All jobs in acme-infra have cost_center", "CI fails without it"])),
        ("approve", "requirements"),
        ("claim",),
        ("sections", {"Plan": "1. Add cost_center to every job file.\n2. Make CI require it."}),
        ("tasks", [{"text": "Add cost_center to every job file", "refs": ["file:infra/jobs/acme_ingest_daily.json"]}]),
        ("approve", "plan"),
        ("start", "T1"),
        ("link", "infra", "chore/DEMO-0025-cost-center-tags", True),
        ("edit", "Plan", "1. Add cost_center to every job file.\n2. Make CI require it.\n"
                         "3. Backfill the tag on the jobs already running on int."),
    )),
    TicketSpec("DEMO-0026", "Make fct_meter_reads incremental", "feature", "high", "m", "claude-code", "i26", 0.60, (
        ("sections", R(["Build fct_meter_reads incrementally by read_at.", "Backfill 2025 once."],
                       ["A nightly run takes under 5 min", "2025 is backfilled and matches the full build"])),
        ("approve", "requirements"),
        ("claim",),
        ("sections", {"Plan": "1. Add the incremental model.\n2. Backfill 2025.\n3. Switch the nightly job."}),
        ("tasks", [{"text": "Add the incremental model", "refs": ["file:dbt/models/marts/fct_meter_reads.sql"]},
                   {"text": "Backfill the 2025 partitions"},
                   {"text": "Grant the dbt job SELECT on raw.meter_reads", "owner": "human"}]),
        ("approve", "plan"),
        ("start", "T1"),
        ("done", "T1", "lint green on feature/DEMO-0026-incremental-reads"),
        ("start", "T2"),
        ("link", "dbt", "feature/DEMO-0026-incremental-reads", True),
        ("ask", [Q("Backfill 2025 in one run or month by month?", "One run needs a large warehouse for about 2 h.",
                   [("A", "One run on a large warehouse", "about CHF 40, 2 h"),
                    ("B", "Month by month", "12 runs over one day")], "B")]),
    )),
    TicketSpec("DEMO-0027", "Handle an empty gateway export file", "bug", "high", "xs", "claude-code", "i27", 0.40, (
        ("sections", R(["An empty export returns no rows instead of crashing."], ["A test covers the empty file"])),
        ("approve", "requirements"),
        ("claim",),
        ("ask", [Q("An empty export: skip it silently or log a warning?", "Ops want to notice dead gateways.",
                   [("A", "Skip silently", "nobody notices a dead gateway"),
                    ("B", "Skip and log a warning", "one log line per empty file")], "B")]),
        ("answer", "Q1", "B", "warn, so ops see dead gateways"),
        ("tasks", [{"text": "Return no rows for an empty export", "refs": ["file:ingest/src/acme_ingest/download.py"],
                    "verify": UNITTEST}]),
        ("start", "T1"),
        ("done", "T1", "test_empty_export passes on fix/DEMO-0027-empty-export"),
        ("link", "ingest", "fix/DEMO-0027-empty-export", True),
        ("sections", {"Verification": f"`{UNITTEST}` in ingest: 14 tests OK, including test_empty_export."}),
        ("artifact", {"name": "empty-export-tests.log", "kind": "log", "label": "Test run with the empty-export tests",
                      "task": "T1", "ac": 1}),
        ("move", "testing"),
    )),
    TicketSpec("DEMO-0028", "Handle DST days in the daily consumption mart", "feature", "normal", "s", "copilot",
               "i28", 0.50, (
        ("sections", R(["Count 23- and 25-hour days correctly in mart_daily_consumption."],
                       ["2026-03-29 has 23 hours of reads", "2026-10-25 has 25 hours of reads"])),
        ("approve", "requirements"),
        ("claim",),
        ("sections", {"Plan": "Skip reads without a timestamp, then test both DST days."}),
        ("tasks", [{"text": "Count 23- and 25-hour days correctly"}, {"text": "Add a test for the 25-hour day 2026-10-25"}]),
        ("approve", "plan"),
        ("start", "T1"),
        ("done", "T1", "fct_meter_reads handles 2026-10-25"),
        ("start", "T2"),
        ("done", "T2", "test added"),
        ("link", "dbt", "feature/DEMO-0028-dst-days", True),
        ("sections", {"Verification": "`python scripts/lint_sql.py` in dbt: green. The 25-hour day 2026-10-25 test passes."}),
        ("artifact", {"name": "dst-25h-day.png", "kind": "screenshot", "label": "Reads per hour on 2026-10-25",
                      "task": "T2", "ac": 2, "inline": True}),
        ("move", "testing"),
        ("verdict", "follow-up", "23-hour days still double-count 02:00; add a test for 2026-03-29."),
        ("tasks", [{"text": "Add a test for the 23-hour day 2026-03-29"}]),
        ("start", "T3"),
    )),
    TicketSpec("DEMO-0029", "Spike: serverless compute for dbt runs", "spike", "low", "s", "claude-code", "i29", 0.30, (
        ("sections", R(["Compare serverless and classic compute for the nightly dbt run."],
                       ["Cost and run time for 10 runs each, in Findings", "A recommendation"])),
        ("approve", "requirements"),
        ("claim",),
        ("sections", {"Plan": "Run the nightly build 10 times on each compute type in dev and compare."}),
        ("tasks", [{"text": "Run 10 builds on each compute type and compare"}]),
        ("approve", "plan"),
        ("start", "T1"),
        ("done", "T1", "numbers in Findings"),
        ("sections", {"Findings": "Serverless is 18% cheaper for runs under 15 min; cold start adds about 40 s. "
                                  "Recommend serverless for the nightly run. The runbook needs the decision (DEMO-0030).",
                      "Verification": "10 nightly builds per compute type in dev; cost and run time per run in Findings."}),
        ("artifact", {"name": "compute-comparison.csv", "kind": "dataset", "label": "Cost and run time, 10 runs each",
                      "task": "T1", "ac": 1}),
        ("move", "testing"),
        ("verdict", "done", None),
    )),
    TicketSpec("DEMO-0030", "Document the serverless decision in the runbook", "chore", "normal", "s", "claude-code",
               None, 0.95, (
        ("raw", {"labels": ["docs"]}),
    ), from_key="DEMO-0029"),
    TicketSpec("DEMO-0031", "Epic: harden the gateway export pipeline", "epic", "high", "l", "claude-code", None,
               0.20, (
        ("sections", R(["Gateway exports that fail transiently are retried, not lost.",
                        "Corrupt exports are rejected before they reach staging.",
                        "Ops hear about a gateway that keeps failing."],
                       ["Every child is done or explicitly dropped", "No export lost in a week of int runs"])),
        ("approve", "requirements", {"delegate": {"max_children": 3, "max_size": "s"}}),
    )),
    TicketSpec("DEMO-0032", "Retry gateway downloads on HTTP 503", "feature", "high", "s", "claude-code", None, 0.18, (
        ("sections", {**R(["Retry a download that answers HTTP 503 up to three times with backoff."],
                          ["A 503 then 200 sequence loads the file", "Three 503s in a row fail the run with the URL"]),
                      "Plan": "Wrap the download call in a retry with 2, 4 and 8 s backoff; test with a fake server."}),
        ("at", 0.24),
        ("claim",),
        ("tasks", [{"text": "Retry 503 responses with backoff", "refs": ["file:ingest/src/acme_ingest/download.py"],
                    "verify": UNITTEST},
                   {"text": "Test the 503-then-200 and three-503 cases", "verify": UNITTEST}]),
        ("start", "T1"),
    ), epic="DEMO-0031"),
    TicketSpec("DEMO-0033", "Validate gateway export checksums", "feature", "normal", "m", "copilot", None, 0.185, (
        ("sections", {**R(["Reject an export whose SHA-256 does not match the gateway's manifest."],
                          ["A corrupt export is rejected with its file name", "Valid exports load as before"]),
                      "Plan": "Read the manifest next to each export and compare hashes before staging."}),
        ("at", 0.40),
        ("edit", "Requirements", "- Reject an export whose SHA-256 does not match the gateway's manifest.\n"
                                 "- Also reject an export that has no manifest entry at all."),
    ), epic="DEMO-0031"),
    TicketSpec("DEMO-0034", "Epic: tariff reporting for Q4", "epic", "normal", "m", "claude-code", None, 0.14, (
        ("sections", R(["Monthly tariff reports for Q4 come from the mart, not from spreadsheets."],
                       ["October, November and December reports run from dbt"])),
        ("approve", "requirements", {"delegate": {}}),
        ("at", 0.60),
        ("pause",),
    )),
    TicketSpec("DEMO-0035", "Monthly tariff summary mart", "feature", "normal", "s", "claude-code", None, 0.12, (
        ("sections", {**R(["Build mart_tariff_monthly with consumption and cost per tariff and month."],
                          ["One row per tariff and month", "Cost matches the tariff table for October"]),
                      "Plan": "Join fct_meter_reads to the tariff seed and aggregate per month."}),
    ), epic="DEMO-0034"),
    TicketSpec("DEMO-0036", "Alert when a gateway fails three runs in a row", "feature", "normal", "s", "claude-code",
               None, 0.45, (
        ("sections", {**R(["Raise an alert when the same gateway fails three consecutive runs."],
                          ["Three failures in a row raise one alert", "A success in between resets the count"]),
                      "Plan": "Count consecutive failures per gateway in the run log and alert at three."}),
        ("auto_approve",),
    ), epic="DEMO-0031", late=True),
)
# Sprints (written into orchestrator/config.json by the seed, dated around the day it runs) and their tickets.
SPRINTS = {
    "S1": ("DEMO-0019", "DEMO-0020", "DEMO-0021", "DEMO-0024", "DEMO-0028", "DEMO-0032"),
    "S2": ("DEMO-0016", "DEMO-0023", "DEMO-0030", "DEMO-0033", "DEMO-0035", "DEMO-0036"),
}
REFRESH = ("DEMO-0002", "DEMO-0004", "DEMO-0009", "DEMO-0019", "DEMO-0020", "DEMO-0021", "DEMO-0024", "DEMO-0028",
           "DEMO-0032")
STALE = ("DEMO-0003", "DEMO-0014", "DEMO-0025")
