import pytest

import seed_proc as sp


@pytest.mark.parametrize("argv", [
    ["git", "push", "--force", "origin", "main"],
    ["git", "-C", "x", "push", "-f", "origin", "b"],
    ["git", "push", "--force-with-lease", "origin", "b"],
    ["git", "push", "origin", "+b"],
    ["git", "push", "origin", ":b"],
    ["git", "push", "--delete", "origin", "b"],
    ["git", "push", "--mirror"],
    ["git", "branch", "-D", "b"],
    ["git", "reset", "--hard", "origin/main"],
    ["git", "clean", "-fdx"],
    ["gh", "repo", "delete", "someone/x"],
    ["gh", "issue", "delete", "3"],
    ["gh", "pr", "merge", "3"],
    ["gh", "pr", "close", "3"],
    ["gh", "api", "-X", "DELETE", "repos/someone/x"],
    ["gh", "api", "--method", "DELETE", "repos/someone/x"],
])
def test_destructive_argv_is_refused(argv):
    assert sp.refuse_reason(argv)


@pytest.mark.parametrize("argv", [
    ["git", "push", "-u", "origin", "feature/DEMO-0020-handle-429"],
    ["git", "-C", "ingest", "push", "origin", "main"],
    ["gh", "pr", "create", "-R", "someone/x", "--head", "b"],
    ["gh", "api", "-X", "PUT", "repos/someone/x/branches/main/protection"],
    ["gh", "issue", "close", "3", "--reason", "completed"],
])
def test_normal_writes_pass(argv):
    assert sp.refuse_reason(argv) is None


def test_dry_run_never_executes(fake_run, capsys):
    w = sp.Writer(apply=False)
    assert w(["gh", "repo", "create", "someone/x", "--private"]) is None
    assert fake_run.calls == []
    assert "PLAN gh repo create someone/x --private" in capsys.readouterr().out


def test_apply_executes_and_refuses_first(fake_run):
    w = sp.Writer(apply=True)
    w(["gh", "repo", "create", "someone/x", "--private"])
    assert fake_run.calls == [["gh", "repo", "create", "someone/x", "--private"]]
    with pytest.raises(sp.SeedError, match="never allowed"):
        w(["git", "push", "--force", "origin", "main"])
    assert len(fake_run.calls) == 1
