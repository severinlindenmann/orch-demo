"""Labels, sprint due dates and issues on the harness repo (the one GH tracker). Existing issues are never edited."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import seed_proc as sp

R = sp.HARNESS_REPO
SPRINT_OFFSETS = {"Sprint 41": -14, "Sprint 42": 5, "Sprint 43": 19}
LABELS = (("area:dbt", "0e8a16", "dbt models"), ("type:investigation", "5319e7", "Find out before deciding"))


@dataclass(frozen=True)
class IssueSpec:
    slug: str
    title: str
    body: str
    labels: tuple
    milestone: str | None
    mine: bool = False
    closed: bool = False


ISSUES: tuple[IssueSpec, ...] = (
    IssueSpec("i16", "Investigate failed acme-ingest-daily runs on int", "Run 9001 failed on int; prod ran fine.",
              ("type:investigation", "area:ingest"), "Sprint 42", mine=True),
    IssueSpec("i17", "Load tariff tables as dbt seeds", "Tariffs are a CSV on a share today.", ("type:feature", "area:dbt"), "Sprint 43"),
    IssueSpec("i18", "Rename the staging schema to stg_acme", "Align with the naming guide.", ("type:chore", "area:dbt"), "Sprint 43"),
    IssueSpec("i19", "Move the gateway download into the ingest service", "Ingest should own downloading.",
              ("type:feature", "area:ingest"), "Sprint 42", mine=True),
    IssueSpec("i20", "Downloader crashes on HTTP 429 without Retry-After", "Seen on gw-07 last night.",
              ("type:bug", "priority:urgent", "area:ingest"), "Sprint 42", mine=True),
    IssueSpec("i21", "Add a meter_type dimension to the dbt marts", "Needed for per-type thresholds.",
              ("type:feature", "area:dbt"), "Sprint 42"),
    IssueSpec("i22", "Use meter_type in the suspect-threshold mart", "Depends on the meter_type dimension.",
              ("type:feature", "area:dbt"), "Sprint 43"),
    IssueSpec("i23", "Show suspect thresholds in the daily report", "Report readers ask which threshold applied.",
              ("type:feature", "area:quality"), "Sprint 43"),
    IssueSpec("i24", "Add the int workspace to the deploy targets", "int exists but has no target yet.",
              ("type:feature", "area:infra"), "Sprint 42"),
    IssueSpec("i25", "Tag every job with cost_center", "Finance needs cost per team.", ("type:chore", "area:infra"), "Sprint 42"),
    IssueSpec("i26", "Make fct_meter_reads incremental", "The full rebuild takes 40 min.",
              ("type:feature", "priority:high", "area:dbt"), "Sprint 42", mine=True),
    IssueSpec("i27", "Handle an empty gateway export file", "An empty export crashes the parser.",
              ("type:bug", "priority:high", "area:ingest"), "Sprint 42", mine=True, closed=True),
    IssueSpec("i28", "Handle DST days in the daily consumption mart", "23- and 25-hour days are counted wrong.",
              ("type:feature", "area:dbt"), "Sprint 42"),
    IssueSpec("i29", "Spike: serverless compute for dbt runs", "Compare cost and run time.", ("type:spike", "area:infra"),
              "Sprint 42", closed=True),
    IssueSpec("n1", "Gateway firmware 4.2 renames the CSV header", "gw-07 sends `kwh_total` instead of `kwh`.",
              ("type:bug", "area:ingest"), "Sprint 42", mine=True),
    IssueSpec("n2", "Add a Grafana panel for the suspect rate", "Ops want a trend.", ("type:feature", "area:quality"), "Sprint 43"),
    IssueSpec("n3", "Rotate the ingest service principal secret", "Expires next month.", ("type:chore", "area:infra"), None, mine=True),
)
CLOSE_COMMENT = "Fixed on the branch; closing ahead of the release."


def ensure_labels(w: sp.Writer) -> None:
    have = {r["name"] for r in sp.jout(["gh", "label", "list", "-R", R, "--limit", "200", "--json", "name"]) or []}
    for name, color, desc in LABELS:
        if name not in have:
            w(["gh", "label", "create", name, "-R", R, "--color", color, "--description", desc])


def ensure_milestones(w: sp.Writer, today: date) -> None:
    rows = sp.jout(["gh", "api", f"repos/{R}/milestones?state=all&per_page=100"]) or []
    by_title = {m["title"]: m for m in rows}
    for title, offset in SPRINT_OFFSETS.items():
        m = by_title.get(title)
        if m is None:
            raise sp.SeedError(f"milestone {title} is missing on {R}; run `seed.py baseline --apply` first")
        if m.get("due_on"):
            continue
        due = (today + timedelta(days=offset)).isoformat() + "T23:59:59Z"
        w(["gh", "api", "-X", "PATCH", f"repos/{R}/milestones/{m['number']}", "-f", f"due_on={due}"])


def all_issues() -> list[dict]:
    return sp.jout(["gh", "issue", "list", "-R", R, "--state", "all", "--limit", "500", "--json", "number,title,state"]) or []


def ensure_issue(spec: IssueSpec, w: sp.Writer, existing: list[dict]) -> int | None:
    found = next((i for i in existing if i["title"] == spec.title), None)
    if found is None:
        argv = ["gh", "issue", "create", "-R", R, "--title", spec.title, "--body", spec.body]
        for label in spec.labels:
            argv += ["--label", label]
        if spec.milestone:
            argv += ["--milestone", spec.milestone]
        if spec.mine:
            argv += ["--assignee", "@me"]
        r = w(argv)
        if r is None:
            return None
        found = {"number": int(r.stdout.strip().rsplit("/", 1)[1]), "state": "OPEN"}
    if spec.closed and found["state"] == "OPEN":
        w(["gh", "issue", "close", str(found["number"]), "-R", R, "--reason", "completed", "--comment", CLOSE_COMMENT])
    return found["number"]


def cmd_issues(args) -> int:
    w = sp.Writer(apply=args.apply)
    sp.require_admin(sp.me())
    ensure_labels(w)
    ensure_milestones(w, date.today())
    existing = all_issues()
    data = sp.load_out()
    for spec in ISSUES:
        number = ensure_issue(spec, w, existing)
        if number is not None:
            data["issues"][spec.slug] = number
    if args.apply:
        sp.save_out(data)
    return 0
