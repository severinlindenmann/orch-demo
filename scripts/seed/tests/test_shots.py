import json
import os
from pathlib import Path

import seed_shots as sh


def test_isolated_env_keeps_the_gh_login(tmp_path, monkeypatch):
    home = tmp_path / "home"
    (home / ".config" / "gh").mkdir(parents=True)
    (home / ".config" / "gh" / "hosts.yml").write_text("github.com: {}\n")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("CLAUDECODE", "1")
    env = sh.isolate_env(tmp_path / "scratch")
    assert Path(os.environ["XDG_CONFIG_HOME"], "gh", "hosts.yml").read_text() == "github.com: {}\n"
    assert os.environ["GH_CONFIG_DIR"] == str(home / ".config" / "gh")
    assert os.environ["ORCH_STATE_DIR"].startswith(str(tmp_path / "scratch"))
    assert "CLAUDECODE" not in os.environ
    assert set(env) >= {"ORCH_STATE_DIR", "XDG_CONFIG_HOME", "GH_CONFIG_DIR"}


def test_enable_addons_writes_only_the_scratch_dir(tmp_path, monkeypatch):
    real = tmp_path / "real-config-orch"
    real.mkdir()
    (real / "workspaces.json").write_text("{}")
    before = sh.config_snapshot(real)
    sh.isolate_env(tmp_path / "scratch")
    root = tmp_path / "ws"
    (root / "orchestrator").mkdir(parents=True)
    settings = json.loads((sh.sp.HERE / "addon_settings.json").read_text())
    sh.enable_addons(root, {k: v for k, v in settings.items() if k in sh.DEFAULT_ADDONS})
    from orch.addons import userfiles
    enabled = userfiles.workspace_addons(root)
    assert set(enabled) == {"github-reviews", "github-issues", "databricks", "wiki"}
    assert all(v["enabled"] for v in enabled.values())
    assert str(userfiles.workspaces_json_path()).startswith(str(tmp_path / "scratch"))
    assert sh.config_snapshot(real) == before


def test_addon_settings_match_the_rulings():
    s = json.loads((sh.sp.HERE / "addon_settings.json").read_text())
    db = s["databricks"]
    assert db["envs"] == {"dev": "acme_dev @ https://adb-5555555555555555.15.azuredatabricks.net",
                          "int": "simulated:int", "prod": "simulated:prod"}
    assert (db["scope"], db["prefixes"], db["demo"]) == ("prefix", "[dev demo] acme-", True)


def test_every_page_and_state_has_a_shot():
    names = {n for n, _, _ in sh.PAGES}
    assert {"today", "board", "board-epic", "board-sprint", "board-list", "board-external", "activity", "reports", "workspace",
            "code-reviews", "databricks", "wiki"} == names
    assert len(sh.TICKET_SHOTS) >= 14


def test_wait_for_caches_asks_the_scheduler_for_a_refresh(tmp_path, monkeypatch):
    class WS:
        state_dir = tmp_path

    class Sched:
        calls = 0

        def request_refresh(self, addon=None):
            Sched.calls += 1
            for n in sh.DEFAULT_ADDONS:  # the first refresh writes every cache
                (tmp_path / "addons" / n).mkdir(parents=True, exist_ok=True)
                (tmp_path / "addons" / n / "x.all.json").write_text("{}")
            return True

    monkeypatch.setattr(sh, "SETTLE_S", 0)
    sh.wait_for_caches(WS(), timeout=5, scheduler=Sched())
    assert Sched.calls >= 1
