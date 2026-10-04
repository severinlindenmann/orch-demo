import json
import re

import pytest

import seed_baseline as sb
import seed_issues as si
import seed_proc as sp

DATA = sb.load()


def test_numbers_are_consecutive_issues_then_prs():
    assert [i["number"] for i in DATA["issues"]] == list(range(1, 16))
    assert [p["number"] for p in DATA["prs"]] == list(range(16, 25))
    assert [p["number"] for p in DATA["prs"] if p["merge"]] == [16, 17]
    assert [p["number"] for p in DATA["prs"] if p["close"]] == [24]


def test_every_number_the_baseline_tickets_cite_is_seeded():
    cited = set()
    base = re.escape(sp.repo_url(sp.HARNESS_REPO))
    for path in (sp.HARNESS / "orchestrator" / "tickets").rglob("DEMO-00*.md"):
        if int(path.name[5:9]) > 15:
            continue
        cited |= {int(n) for n in re.findall(base + r"/(?:issues|pull)/(\d+)", path.read_text(encoding="utf-8"))}
    assert cited and cited <= set(range(1, 25))


def test_labels_and_milestones_used_exist():
    made = {lb["name"] for lb in DATA["labels"]} | {name for name, _, _ in si.LABELS}
    used = {lb for item in DATA["issues"] + DATA["prs"] for lb in item["labels"]}
    assert used <= made
    assert {i["milestone"] for i in DATA["issues"]} - {None} <= {m["title"] for m in DATA["milestones"]}
    assert set(si.SPRINT_OFFSETS) == {m["title"] for m in DATA["milestones"]}


def test_closed_items_say_why():
    assert all(i["comment"] for i in DATA["issues"] if i["closed"])
    assert all(p["comment"] for p in DATA["prs"] if p["close"])


def test_only_the_baseline_writer_may_close_a_pr_and_nobody_merges():
    close = ["gh", "pr", "close", "24", "-R", "someone/x"]
    assert sp.refuse_reason(close)
    assert sp.refuse_reason(close, sb.ALLOW) is None
    assert sp.refuse_reason(["gh", "pr", "merge", "16"], sb.ALLOW)
    assert sp.refuse_reason(["git", "-C", "d", *sp.GIT_ID, "push", "--force"]) is not None


def test_seeded_commits_use_the_configured_identity_not_the_global_config():
    assert sp.GIT_ID == ("-c", f"user.name={sp.GIT_NAME}", "-c", f"user.email={sp.GIT_EMAIL}")
    assert sp._git_sub(["git", "-C", "d", *sp.GIT_ID, "commit", "-m", "x"]) == ("commit", ["-m", "x"])


def _empty_repo(fake_run, gh_login, rows=()):
    fake_run.answer(["gh", "api", "user"], gh_login)
    fake_run.answer(["gh", "api", f"repos/{sp.HARNESS_REPO}", "--jq"], json.dumps({"admin": True}))
    fake_run.answer(["gh", "label", "list"], "[]")
    fake_run.answer(["gh", "api", f"repos/{sp.HARNESS_REPO}/milestones?state=all&per_page=100"], "[]")
    fake_run.answer(["gh", "api", f"repos/{sp.HARNESS_REPO}/issues?state=all&per_page=100"], json.dumps(list(rows)))


def test_dry_run_on_an_empty_repo_plans_everything_in_number_order(fake_run, gh_login, capsys, monkeypatch, tmp_path):
    monkeypatch.setattr(sb, "clone_dir", lambda: tmp_path / "none")
    _empty_repo(fake_run, gh_login)
    assert sb.cmd_baseline(type("A", (), {"apply": False})()) == 0
    assert fake_run.writes() == []
    out = capsys.readouterr().out
    titles = [i["title"] for i in DATA["issues"]] + [p["title"] for p in DATA["prs"]]
    positions = [out.index(f"--title {t}" if " " not in t else f"--title '{t}'") for t in titles]
    assert positions == sorted(positions)
    assert "PLAN close milestone Sprint 41" in out and "state=closed" not in out
    assert "PLAN close #24" in out and "PLAN gh issue close 7" in out and "PLAN merge #16" in out and "PLAN merge #17" in out


def test_refuses_a_repo_that_already_has_other_issues(fake_run, gh_login, monkeypatch, tmp_path):
    monkeypatch.setattr(sb, "clone_dir", lambda: tmp_path / "none")
    _empty_repo(fake_run, gh_login, rows=[{"number": 1, "title": "Something else", "state": "open"}])
    with pytest.raises(sp.SeedError, match="expected"):
        sb.cmd_baseline(type("A", (), {"apply": False})())


def test_refuses_when_the_next_number_would_be_wrong(fake_run, gh_login, monkeypatch, tmp_path):
    monkeypatch.setattr(sb, "clone_dir", lambda: tmp_path / "none")
    _empty_repo(fake_run, gh_login, rows=[{"number": 3, "title": DATA["issues"][2]["title"], "state": "open"}])
    with pytest.raises(sp.SeedError, match="next number"):
        sb.cmd_baseline(type("A", (), {"apply": False})())


def test_rerun_after_the_baseline_writes_nothing(fake_run, gh_login, monkeypatch, tmp_path):
    monkeypatch.setattr(sb, "clone_dir", lambda: tmp_path / "none")
    rows = [{"number": i["number"], "title": i["title"], "state": "closed" if i["closed"] else "open"} for i in DATA["issues"]]
    rows += [{"number": p["number"], "title": p["title"], "state": "closed" if p["merge"] or p["close"] else "open"}
             for p in DATA["prs"]]
    _empty_repo(fake_run, gh_login, rows=rows)
    fake_run.answer(["gh", "label", "list"], json.dumps([{"name": lb["name"]} for lb in DATA["labels"]]))
    fake_run.answer(["gh", "api", f"repos/{sp.HARNESS_REPO}/milestones?state=all&per_page=100"],
                    json.dumps([{"title": m["title"]} for m in DATA["milestones"]]))
    fake_run.answer(["gh", "issue", "view"], json.dumps({"comments": [{"body": "x"}]}))
    fake_run.answer(["gh", "pr", "view"], json.dumps({"state": "MERGED", "comments": [{"body": "x"}]}))
    w = sp.Writer(apply=True, allow=sb.ALLOW)
    have = sb.numbered()
    for spec in DATA["issues"]:
        sb.ensure_issue(spec, w, have)
    for spec in DATA["prs"]:
        sb.ensure_pr(spec, None, w, have)
    assert w.log == [] and fake_run.writes() == []
