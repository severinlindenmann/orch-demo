import json
import shutil
import subprocess
import sys

import pytest

import seed_files as sf
import seed_proc as sp
import seed_repos as sr


@pytest.mark.parametrize("name", ["ingest", "dbt", "infra"])
def test_main_tree_passes_its_own_ci(tmp_path, name):
    sr.write_tree(tmp_path, sf.MAIN_TREES[name])
    cmd = sf.CI_COMMANDS[name].split()
    r = subprocess.run([sys.executable, *cmd[1:]], cwd=tmp_path, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


@pytest.mark.parametrize("name", ["ingest", "dbt", "infra"])
def test_main_tree_ships_ci_and_bot(name):
    tree = sf.MAIN_TREES[name]
    assert ".github/workflows/ci.yml" in tree and ".github/workflows/demo-bot.yml" in tree
    assert sf.CI_COMMANDS[name] in tree[".github/workflows/ci.yml"]
    assert "${{ inputs." not in tree[".github/workflows/demo-bot.yml"].split("steps:")[1]  # inputs only via env


def test_existing_repo_and_main_are_only_checked(fake_run, tmp_path, monkeypatch):
    clone = tmp_path / "ingest"
    (clone / ".git").mkdir(parents=True)
    monkeypatch.setattr(sr, "clone_dir", lambda name: clone)
    fake_run.answer(["gh", "repo", "view"], json.dumps({"name": sp.subrepo("ingest").split("/")[1]}))
    fake_run.answer(["git", "-C", str(clone), "remote", "get-url"], f"git@github.com:{sp.subrepo('ingest')}.git")
    fake_run.answer(["git", "-C", str(clone), "ls-remote"], "abc\trefs/heads/main")
    fake_run.answer(["gh", "api", f"repos/{sp.subrepo('ingest')}/actions/permissions/workflow"],
                    json.dumps({"can_approve_pull_request_reviews": True}))
    fake_run.answer(["gh", "api", f"repos/{sp.subrepo('ingest')}/branches/main/protection"], "{}")
    assert sr.ensure_subrepo("ingest", sp.Writer(apply=True))
    assert fake_run.writes() == []


def test_missing_repo_is_created_private_and_dry_run_stops(fake_run):
    fake_run.answer(["gh", "repo", "view"], "", code=1)
    assert sr.ensure_subrepo("dbt", sp.Writer(apply=False)) is False
    assert fake_run.writes() == []  # dry run: printed only


def test_actions_policy_refusal_stops_with_the_setting_name(fake_run):
    fake_run.answer(["gh", "api", f"repos/{sp.subrepo('infra')}/actions/permissions/workflow"],
                    json.dumps({"can_approve_pull_request_reviews": False}))
    fake_run.answer(["gh", "api", "-X", "PUT"], "", code=1)
    with pytest.raises(sp.SeedError, match="Allow GitHub Actions to create and approve pull requests"):
        sr.ensure_actions_can_review(sp.subrepo("infra"), sp.Writer(apply=True))


def test_protection_is_put_once(fake_run):
    fake_run.answer(["gh", "api", f"repos/{sp.subrepo('dbt')}/branches/main/protection"], "", code=1)
    sr.ensure_protection(sp.subrepo("dbt"), sp.Writer(apply=True))
    put = [c for c in fake_run.calls if "-X" in c]
    assert put == [["gh", "api", "-X", "PUT", f"repos/{sp.subrepo('dbt')}/branches/main/protection", "--input", "-"]]


def test_clone_refuses_a_foreign_folder(tmp_path, monkeypatch, fake_run):
    folder = tmp_path / "infra"
    folder.mkdir()
    (folder / "notes.txt").write_text("mine")
    monkeypatch.setattr(sr, "clone_dir", lambda name: folder)
    with pytest.raises(sp.SeedError, match="not a git clone"):
        sr.ensure_clone("infra", sp.Writer(apply=True))


def test_a_policy_refusal_still_seeds_every_repo_and_exits_nonzero(monkeypatch, fake_run):
    done = []

    def fake_subrepo(name, w):
        done.append(name)
        raise sr.PolicyError("Allow GitHub Actions to create and approve pull requests")

    monkeypatch.setattr(sr, "ensure_subrepo", fake_subrepo)
    fake_run.answer(["gh", "api", f"repos/{sp.HARNESS_REPO}", "--jq"], json.dumps({"admin": True}))

    class Args:
        apply = True

    assert sr.cmd_repos(Args()) == 3
    assert done == ["ingest", "dbt", "infra"]


def test_protection_runs_before_the_actions_setting(fake_run, tmp_path, monkeypatch):
    clone = tmp_path / "dbt"
    (clone / ".git").mkdir(parents=True)
    monkeypatch.setattr(sr, "clone_dir", lambda name: clone)
    fake_run.answer(["git", "-C", str(clone), "remote", "get-url"], f"git@github.com:{sp.subrepo('dbt')}.git")
    fake_run.answer(["git", "-C", str(clone), "ls-remote"], "abc\trefs/heads/main")
    fake_run.answer(["gh", "api", f"repos/{sp.subrepo('dbt')}/branches/main/protection"], "", code=1)
    fake_run.answer(["gh", "api", f"repos/{sp.subrepo('dbt')}/actions/permissions/workflow"],
                    json.dumps({"can_approve_pull_request_reviews": False}))
    fake_run.answer(["gh", "api", "-X", "PUT", f"repos/{sp.subrepo('dbt')}/actions"], "", code=1)
    with pytest.raises(sr.PolicyError):
        sr.ensure_subrepo("dbt", sp.Writer(apply=True))
    puts = [c[4] for c in fake_run.calls if "-X" in c]
    assert puts == [f"repos/{sp.subrepo('dbt')}/branches/main/protection",
                    f"repos/{sp.subrepo('dbt')}/actions/permissions/workflow"]
