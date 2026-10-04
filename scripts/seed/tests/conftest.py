import os
import sys
from pathlib import Path

import pytest

SEED = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SEED))
from seed_scratch import AGENT_VARS, SCRATCH_MARK  # noqa: E402


@pytest.fixture(autouse=True)
def _isolated(monkeypatch, tmp_path_factory):
    for var in AGENT_VARS + ("GH_CONFIG_DIR",):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("ORCH_STATE_DIR", str(tmp_path_factory.mktemp("orch-user")))
    # every test dir is a scratch dir: run_all(sign_earlier=True) and seed_scratch.prepare accept it
    monkeypatch.setenv(SCRATCH_MARK, str(tmp_path_factory.getbasetemp().resolve()))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path_factory.mktemp("xdg")))
    # git in tests must not read the user's global config (signing, hooksPath, templates)
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    # The suite may run under an agent harness: its real process tree must not decide who acts (the same stub as
    # orch-core's tests/conftest.py). Tests of the ancestry refusal replace it with their own chain.
    import orch.actor
    monkeypatch.setattr(orch.actor, "process_chain", lambda: [])


@pytest.fixture
def fake_run(monkeypatch):
    import seed_proc
    from fakes import FakeRun
    fake = FakeRun()
    monkeypatch.setattr(seed_proc, "run", fake)
    return fake


GH_LOGIN = "demo-user"  # the gh account the tests pretend to be: a fixture value, never a real account


@pytest.fixture
def gh_login():
    return GH_LOGIN
