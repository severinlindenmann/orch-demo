import json
from datetime import date

import seed_issues as si
import seed_proc as sp


def test_existing_issue_is_not_created_again(fake_run):
    spec = si.ISSUES[0]
    assert si.ensure_issue(spec, sp.Writer(apply=True), [{"number": 31, "title": spec.title, "state": "OPEN"}]) == 31
    assert fake_run.writes() == []


def test_closed_spec_closes_an_open_issue_once(fake_run):
    spec = next(s for s in si.ISSUES if s.closed)
    si.ensure_issue(spec, sp.Writer(apply=True), [{"number": 40, "title": spec.title, "state": "OPEN"}])
    si.ensure_issue(spec, sp.Writer(apply=True), [{"number": 40, "title": spec.title, "state": "CLOSED"}])
    closes = [c for c in fake_run.calls if c[:3] == ["gh", "issue", "close"]]
    assert len(closes) == 1 and "--reason" in closes[0]


def test_new_issue_number_comes_from_the_url(fake_run):
    fake_run.answer(["gh", "issue", "create"], f"https://github.com/{sp.HARNESS_REPO}/issues/42\n")
    spec = next(s for s in si.ISSUES if s.mine)
    assert si.ensure_issue(spec, sp.Writer(apply=True), []) == 42
    create = next(c for c in fake_run.calls if c[:3] == ["gh", "issue", "create"])
    assert ["--assignee", "@me"] == create[create.index("--assignee"):create.index("--assignee") + 2]


def test_milestones_with_a_due_date_are_left_alone(fake_run):
    rows = [{"number": 1, "title": "Sprint 41", "due_on": "2026-09-20T23:59:59Z"},
            {"number": 2, "title": "Sprint 42", "due_on": None},
            {"number": 3, "title": "Sprint 43", "due_on": None}]
    fake_run.answer(["gh", "api", f"repos/{sp.HARNESS_REPO}/milestones?state=all&per_page=100"], json.dumps(rows))
    si.ensure_milestones(sp.Writer(apply=True), date(2026, 10, 5))
    patches = [c for c in fake_run.calls if "PATCH" in c]
    assert [p[4] for p in patches] == [f"repos/{sp.HARNESS_REPO}/milestones/2", f"repos/{sp.HARNESS_REPO}/milestones/3"]
    assert "due_on=2026-10-10T23:59:59Z" in patches[0]


def test_no_issue_targets_the_closed_sprint():
    assert all(s.milestone in ("Sprint 42", "Sprint 43", None) for s in si.ISSUES)


def test_mine_and_not_imported_and_out_of_sync_exist():
    assert any(s.mine and not s.closed for s in si.ISSUES)
    assert {"n1", "n2", "n3"} <= {s.slug for s in si.ISSUES}
    assert any(s.closed and s.slug == "i27" for s in si.ISSUES)
