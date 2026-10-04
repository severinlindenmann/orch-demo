import json
import subprocess
import sys
from collections import Counter

import pytest

import seed_checklist as cl
import seed_files as sf
import seed_proc as sp
import seed_prs as spr
import seed_repos as sr


def _tree_after(spec):
    tree = dict(sf.MAIN_TREES[spec.repo])
    tree.update(spec.files)
    return tree


@pytest.mark.parametrize("spec", sf.PR_SPECS, ids=lambda s: f"{s.repo}:{s.branch}")
def test_ci_fails_only_on_the_failing_branches(tmp_path, spec):
    sr.write_tree(tmp_path, _tree_after(spec))
    cmd = sf.CI_COMMANDS[spec.repo].split()
    r = subprocess.run([sys.executable, *cmd[1:]], cwd=tmp_path, capture_output=True, text=True)
    assert (r.returncode != 0) == (spec.state == "failing"), r.stdout + r.stderr


def test_every_repo_has_every_state_one_account_can_seed():
    assert len(sf.PR_SPECS) == 16
    for repo in ("ingest", "dbt", "infra"):
        states = Counter(s.seeded_state for s in sf.PR_SPECS if s.repo == repo)
        for want in ("failing", "draft", "conflict"):
            assert states[want] == 1, (repo, want)
        assert states["open"] >= 2, repo  # open, passing, no review
    assert any(s.state == "changes_requested" for s in sf.PR_SPECS if s.repo == "dbt")


def test_review_states_are_seeded_as_open_without_review():
    for s in sf.PR_SPECS:
        assert (s.seeded_state == "open") == (s.state in sf.NEEDS_SECOND_ACCOUNT)
        assert s.seeded_state in s.body or "open, no review yet" in s.body


def _git(d, *args):
    return subprocess.run(["git", "-C", str(d), *args], capture_output=True, text=True, check=False)


@pytest.mark.parametrize("spec", [s for s in sf.PR_SPECS if s.state == "conflict"], ids=lambda s: s.repo)
def test_conflict_specs_really_conflict(tmp_path, spec):
    d = tmp_path / "r"
    d.mkdir()
    _git(d, "init", "-q", "-b", "main")
    _git(d, "config", "user.email", "t@example.com")
    _git(d, "config", "user.name", "t")
    sr.write_tree(d, sf.MAIN_TREES[spec.repo])
    _git(d, "add", "-A")
    _git(d, "commit", "-qm", "base")
    _git(d, "switch", "-qc", spec.branch)
    sr.write_tree(d, spec.files)
    _git(d, "commit", "-qam", "branch")
    _git(d, "switch", "-q", "main")
    sr.write_tree(d, spec.main_commit["files"])
    _git(d, "commit", "-qam", "main")
    assert _git(d, "merge", "--no-commit", spec.branch).returncode != 0


def test_titles_cite_only_planned_ticket_keys():
    for s in sf.PR_SPECS:
        if s.ticket:
            assert s.title.removeprefix("Draft: ").startswith(s.ticket + " ") and s.ticket in s.branch
        else:
            assert "DEMO-" not in s.title


def _spec(state="approved"):
    return next(s for s in sf.PR_SPECS if s.repo == "ingest" and s.state == state)


def test_pushed_branch_without_pr_only_creates_the_pr(fake_run, tmp_path, monkeypatch, gh_login):
    spec = _spec("draft")
    monkeypatch.setattr(spr, "clone_dir", lambda name: tmp_path)
    fake_run.answer(["git", "-C", str(tmp_path), "ls-remote"], f"abc\trefs/heads/{spec.branch}")
    fake_run.answer(["gh", "pr", "list"], "[]")
    spr.ensure_branch(spec, sp.Writer(apply=True))
    w = sp.Writer(apply=False)
    spr.ensure_pr(spec, w, gh_login)
    assert not any("push" in c or "commit" in c for c in fake_run.calls)
    assert len(w.log) == 1 and w.log[0][:3] == ["gh", "pr", "create"] and "--draft" in w.log[0]


def test_local_branch_not_pushed_is_pushed_not_recreated(fake_run, tmp_path, monkeypatch):
    spec = _spec("approved")
    monkeypatch.setattr(spr, "clone_dir", lambda name: tmp_path)
    fake_run.answer(["git", "-C", str(tmp_path), "ls-remote"], "")
    fake_run.answer(["git", "-C", str(tmp_path), "rev-parse", "--verify", "--quiet", f"refs/heads/{spec.branch}"], "abc")
    spr.ensure_branch(spec, sp.Writer(apply=True))
    assert not any("switch" in c and "-c" in c for c in fake_run.calls)
    assert ["git", "-C", str(tmp_path), "push", "-u", "origin", spec.branch] in fake_run.calls


@pytest.mark.parametrize("state", sorted(sf.NEEDS_SECOND_ACCOUNT | {"failing", "draft", "conflict"}))
def test_prs_are_opened_by_the_user_without_bot_or_review(fake_run, state, gh_login):
    spec = next(s for s in sf.PR_SPECS if s.state == state)
    fake_run.answer(["gh", "pr", "list"], "[]")
    w = sp.Writer(apply=False)
    spr.ensure_pr(spec, w, gh_login)
    assert len(w.log) == 1 and w.log[0][:3] == ["gh", "pr", "create"]
    assert ("--draft" in w.log[0]) == (state == "draft")
    assert "--reviewer" not in w.log[0]
    assert not any(c[:3] == ["gh", "workflow", "run"] or c[:3] == ["gh", "pr", "review"] for c in fake_run.calls)


def test_existing_pr_is_left_alone(fake_run, gh_login):
    spec = _spec("conflict")
    fake_run.answer(["gh", "pr", "list"], json.dumps([{"number": 5, "url": "u", "state": "OPEN", "isDraft": False}]))
    assert spr.ensure_pr(spec, sp.Writer(apply=True), gh_login) == {"number": 5, "url": "u"}
    assert fake_run.writes() == []


def test_main_commit_already_on_main_is_not_made_again(fake_run, tmp_path, monkeypatch):
    spec = _spec("conflict")
    monkeypatch.setattr(spr, "clone_dir", lambda name: tmp_path)
    fake_run.answer(["git", "-C", str(tmp_path), "log", "origin/main"], f"{spec.main_commit['subject']}\nScaffold")
    spr.ensure_main_commit(spec, sp.Writer(apply=True))
    assert fake_run.writes() == []


def _row(branch, **kw):
    ok = [{"__typename": "CheckRun", "status": "COMPLETED", "conclusion": "SUCCESS", "detailsUrl": "https://x"}]
    return {"headRefName": branch, "isDraft": False, "reviewDecision": "REVIEW_REQUIRED", "reviewRequests": [],
            "mergeable": "MERGEABLE", "statusCheckRollup": ok, **kw}


def test_pr_checklist_accepts_the_seeded_states_and_allows_the_review_states(fake_run, gh_login):
    bad = [{"__typename": "CheckRun", "status": "COMPLETED", "conclusion": "FAILURE", "detailsUrl": "https://x"}]
    fake_run.answer(["gh", "api", "user"], gh_login)
    for name, full in sr.SUBREPOS.items():
        rows = []
        for s in (s for s in sf.PR_SPECS if s.repo == name):
            st = s.seeded_state
            rows.append(_row(s.branch, isDraft=st == "draft", mergeable="CONFLICTING" if st == "conflict" else "MERGEABLE",
                             statusCheckRollup=bad if st == "failing" else _row("")["statusCheckRollup"]))
        fake_run.answer(["gh", "pr", "list", "-R", full], json.dumps(rows))
    found = cl.pr_problems(None)
    assert all(isinstance(p, cl.Allowed) for p in found), found
    assert sorted(p.split(":", 1)[0] for p in found) == ["approved", "changes_requested", "review_requested"]
    assert all(sf.SECOND_ACCOUNT_HINT in p for p in found)


def test_pr_checklist_flags_a_missing_pr_and_a_wrong_state(fake_run, gh_login):
    fake_run.answer(["gh", "api", "user"], gh_login)
    first = next(s for s in sf.PR_SPECS if s.repo == "ingest" and s.seeded_state == "draft")
    fake_run.answer(["gh", "pr", "list", "-R", sr.SUBREPOS["ingest"]], json.dumps([_row(first.branch)]))
    real = [p for p in cl.pr_problems(None) if not isinstance(p, cl.Allowed)]
    assert any("want ['draft']" in p for p in real)
    assert any("no open PR for fix/DEMO-0020-handle-429" in p for p in real)
    assert any(f"{sp.subrepo('dbt')}: no PR with passing checks" in p for p in real)


def test_the_seed_never_calls_the_demo_bot():
    # demo-bot.yml stays on the sub-repos' main (workflow_dispatch only, so it never runs by itself); the seed no longer calls it
    import inspect
    assert "demo-bot" not in inspect.getsource(spr)
