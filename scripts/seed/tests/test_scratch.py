import os
from pathlib import Path

import pytest

import seed_proc as sp
import seed_scratch as sc
import seed_shots as sh


def test_hook_needs_an_isolated_env(tmp_path, monkeypatch):
    monkeypatch.delenv(sc.SCRATCH_MARK, raising=False)
    with pytest.raises(sp.SeedError, match="isolate_env"):
        with sc.scratch_human(tmp_path / "ws"):
            pass


def test_hook_refuses_the_real_demo_and_outside_dirs(tmp_path, monkeypatch):
    sc.isolate_env(tmp_path / "scratch")
    with pytest.raises(sp.SeedError, match="scratch copy"):
        sc.check_scratch(sp.HARNESS)
    with pytest.raises(sp.SeedError, match="scratch copy"):
        sc.check_scratch(tmp_path / "elsewhere")
    monkeypatch.setenv("ORCH_STATE_DIR", str(tmp_path / "not-scratch"))
    with pytest.raises(sp.SeedError, match="ORCH_STATE_DIR"):
        sc.check_scratch(tmp_path / "scratch" / "ws")


def test_hook_refuses_agent_markers(tmp_path, monkeypatch):
    sc.isolate_env(tmp_path / "scratch")
    monkeypatch.setenv("CLAUDECODE", "1")
    with pytest.raises(sp.SeedError, match="agent markers"):
        with sc.scratch_human(tmp_path / "scratch" / "ws"):
            pass


def test_hook_lets_human_ops_run_under_an_agent_ancestor_only_inside(tmp_path, monkeypatch):
    import orch.actor
    from orch.actor import agent_harness
    monkeypatch.setattr(orch.actor, "process_chain", lambda: [(1, "claude")])
    sc.isolate_env(tmp_path / "scratch")
    assert agent_harness() == "claude-code"
    with sc.scratch_human(tmp_path / "scratch" / "ws"):
        assert agent_harness() is None
    assert agent_harness() == "claude-code"


def test_shots_use_the_scratch_env(tmp_path):
    assert sh.isolate_env is sc.isolate_env
    sc.isolate_env(tmp_path / "scratch")
    assert os.environ[sc.SCRATCH_MARK] == str((tmp_path / "scratch").resolve())
    assert Path(os.environ["ORCH_STATE_DIR"]).is_relative_to(Path(os.environ[sc.SCRATCH_MARK]))


def test_a_rehearsal_ledger_is_carried_into_the_scratch_dir(tmp_path):
    reh = tmp_path / "reh"
    (reh / "orch-user").mkdir(parents=True)
    (reh / "orch-user" / "ledger.key").write_bytes(b"k" * 32)
    (reh / "orch-user" / "ledger.jsonl").write_text("{}\n")
    sc.isolate_env(tmp_path / "scratch")
    assert sc.carry_rehearsal_ledger(reh / sp.HARNESS_NAME) is False  # no rehearsal report: not a rehearsal
    (reh / "rehearsal-report.json").write_text("{}")
    assert sc.carry_rehearsal_ledger(reh / sp.HARNESS_NAME) is True
    assert (Path(os.environ["ORCH_STATE_DIR"]) / "ledger.key").read_bytes() == b"k" * 32
    assert sc.carry_rehearsal_ledger(None) is False
