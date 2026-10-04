import json
from pathlib import Path
import shutil
import subprocess
import tarfile
from datetime import timedelta
from io import BytesIO

import pytest

import seed_proc as sp
import seed_specs as ss
import seed_tickets as st


def _baseline_rev() -> str:
    """The repo's initial commit: its orchestrator/ is the baseline (DEMO-0001..0015) the seed builds on."""
    roots = subprocess.run(["git", "-C", str(sp.HARNESS), "rev-list", "--max-parents=0", "HEAD"],
                           capture_output=True, text=True, check=True).stdout.split()
    return roots[-1]


def _fake_out():
    issues = {f"i{n}": 100 + n for n in range(16, 30)}
    from seed_files import PR_SPECS
    prs = {f"{s.repo}:{s.branch}": {"number": i + 1, "url": f"https://github.com/{sp.subrepo(s.repo)}/pull/{i + 1}"}
           for i, s in enumerate(PR_SPECS)}
    return {"issues": issues, "prs": prs}


@pytest.fixture
def demo_ws(tmp_path):
    """The demo's orchestrator/ as of the initial commit (the baseline), with the current config."""
    raw = subprocess.run(["git", "-C", str(sp.HARNESS), "archive", _baseline_rev(), "orchestrator"], capture_output=True, check=True).stdout
    tarfile.open(fileobj=BytesIO(raw)).extractall(tmp_path, filter="data")
    shutil.copy(sp.HARNESS / "orchestrator" / "config.json", tmp_path / "orchestrator" / "config.json")
    for spec in ss.TICKETS:  # the task refs point into the harness and its sub-repos: stub them
        for step in spec.steps:
            for task in step[1] if step[0] == "tasks" else ():
                for ref in task.get("refs") or ():
                    stub = tmp_path / ref.removeprefix("file:")
                    stub.parent.mkdir(parents=True, exist_ok=True)
                    stub.touch()
    from orch.core.workspace import Workspace
    return Workspace.open(tmp_path)


def _build(ws):
    # the real path: the timeline runs from the baseline's last event (2026-10-02T07:47Z) to now
    return st.run_all(ws, st.Refs(_fake_out()), sign_earlier=True)


def test_build_reaches_every_state(demo_ws):
    import seed_checklist as cl
    ids = _build(demo_ws)
    assert sorted(ids.values()) == [f"DEMO-{n:04d}" for n in range(16, 37)]
    assert cl.ticket_problems(demo_ws) == []


def test_epics_children_and_delegation(demo_ws):
    from orch.core import epics, ledger, store
    from orch.core.events import read_events
    _build(demo_ws)

    def load(k):
        return store.load(demo_ws, k)[1]
    gateway, tariff = load("DEMO-0031"), load("DEMO-0034")
    assert {c.id for c in epics.children(demo_ws, "DEMO-0031")} == {"DEMO-0032", "DEMO-0033", "DEMO-0036"}
    states = {k: epics.child_state(demo_ws, gateway, load(k)) for k in ("DEMO-0032", "DEMO-0033", "DEMO-0036")}
    assert states == {"DEMO-0032": "covered", "DEMO-0033": "changed", "DEMO-0036": "delegated"}
    assert load("DEMO-0032").status == "in-progress" and load("DEMO-0036").status == "open"
    assert epics.delegation(demo_ws, gateway)["paused"] is False
    assert epics.delegation(demo_ws, tariff)["paused"] is True
    # the charters and the pause are the human's signed decisions; the auto-approval is the agent's event
    signed = ledger.entries(demo_ws)
    assert {e["ticket"] for e in signed if e["kind"] == "charter"} == {"DEMO-0031", "DEMO-0034"}
    assert any(e["kind"] == "pause" and e["ticket"] == "DEMO-0034" for e in signed)
    delegated = [e for e in read_events(demo_ws) if e.kind == "gate.delegated"]
    assert delegated and all(e.ticket == "DEMO-0036" and str(e.actor).startswith("agent:") for e in delegated)


def test_sprints_current_and_next(demo_ws):
    from orch.core import sprints, store
    _build(demo_ws)
    cur = sprints.current(demo_ws)
    assert cur and cur["id"] == "S1"
    by_sprint = {}
    for e in store.scan(demo_ws):
        if e.meta and e.meta.get("sprint"):
            by_sprint.setdefault(e.meta["sprint"], set()).add(e.id)
    assert by_sprint == {k: set(v) for k, v in ss.SPRINTS.items()}


def test_sprint_dates_cover_today_from_monday():
    from datetime import date
    s1, s2 = st.sprint_dates(date(2026, 10, 4))
    assert (s1["start"], s1["end"], s2["start"], s2["end"]) == ("2026-09-28", "2026-10-11", "2026-10-12", "2026-10-25")


def test_segments_run_epic_children_around_the_approval():
    order = [(s.key, steps[0][0] if steps else None) for _, s, steps in st.segments(ss.TICKETS)
             if s.key in ("DEMO-0031", "DEMO-0032", "DEMO-0033", "DEMO-0036")]
    keys = [k for k, _ in order]
    assert keys.index("DEMO-0032") < keys.index("DEMO-0031") < keys.index("DEMO-0036")
    assert order[keys.index("DEMO-0031") + 1] == ("DEMO-0032", "claim")


def test_only_expected_check_findings(demo_ws):
    import seed_checklist as cl
    _build(demo_ws)
    assert cl.check_problems(demo_ws) == []


def test_rerun_is_a_no_op(demo_ws):
    _build(demo_ws)
    events = (demo_ws.state_dir / "events.jsonl").read_text()
    from orch.clock import now
    st.migrate_external(demo_ws, st.Ops(demo_ws, st.HUMAN))
    st.build(demo_ws, st.Refs(_fake_out()), human=st.HUMAN, start=now() - timedelta(hours=30), end=now())
    assert (demo_ws.state_dir / "events.jsonl").read_text() == events


def test_counter_shift_aborts_before_writing(demo_ws):
    st.Ops(demo_ws, st.agent_actor(ss.TICKETS[0])).new("Somebody else's ticket")
    before = (demo_ws.state_dir / "events.jsonl").read_text()
    from orch.clock import now
    with pytest.raises(sp.SeedError, match="DEMO-0017"):
        st.build(demo_ws, st.Refs(_fake_out()), human=st.HUMAN, start=now() - timedelta(hours=30), end=now())
    assert (demo_ws.state_dir / "events.jsonl").read_text() == before


def test_short_window_aborts(demo_ws):
    from orch.clock import now
    with pytest.raises(sp.SeedError, match="6 h"):
        st.build(demo_ws, st.Refs(_fake_out()), human=st.HUMAN, start=now() - timedelta(hours=2), end=now())


def test_stale_claim_is_stale_at_the_end(demo_ws):
    from orch.core import store
    from orch.core.ops import claim_expired
    _build(demo_ws)
    for key in ss.STALE:
        _, t = store.load(demo_ws, key)
        assert claim_expired(t.meta["claim"], 4), key


def test_refresh_makes_claims_fresh(demo_ws):
    from orch.core import store
    from orch.core.ops import claim_expired
    _build(demo_ws)
    for key in ss.REFRESH:
        _, t = store.load(demo_ws, key)
        assert not claim_expired(t.meta["claim"], 4), key


def test_events_are_in_time_order(demo_ws):
    _build(demo_ws)
    ats = [json.loads(line)["at"] for line in (demo_ws.state_dir / "events.jsonl").read_text().splitlines()
           if json.loads(line)["kind"] != "ledger.adopted"]
    assert ats == sorted(ats)


def test_no_bare_keys_after_migration(demo_ws):
    from orch.core import store
    st.migrate_external(demo_ws, st.Ops(demo_ws, st.HUMAN))
    keys = [x["key"] for e in store.scan(demo_ws) for x in e.meta.get("external") or []]
    assert keys and all(k.startswith("GH-") for k in keys)
    assert st.migrate_external(demo_ws, st.Ops(demo_ws, st.HUMAN)) == []


def test_specs_match_pr_and_issue_specs():
    from seed_files import PR_SPECS
    from seed_issues import ISSUES
    branches = {(s.repo, s.branch) for s in PR_SPECS}
    slugs = {i.slug for i in ISSUES}
    for spec in ss.TICKETS:
        assert spec.issue is None or spec.issue in slugs
        for step in spec.steps:
            if step[0] == "link" and step[3]:
                assert (step[1], step[2]) in branches, step


def test_apply_refuses_inside_an_agent(monkeypatch):
    import argparse
    monkeypatch.setenv("CLAUDECODE", "1")
    monkeypatch.setattr(st, "rehearse", lambda *a, **k: pytest.fail("must refuse before the rehearsal"))
    monkeypatch.setattr(st, "run_all", lambda *a, **k: pytest.fail("must never write the demo from an agent"))
    with pytest.raises(sp.SeedError, match="agent harness"):
        st.cmd_tickets(argparse.Namespace(apply=True))


def test_apply_refuses_without_a_terminal(monkeypatch):
    import argparse
    monkeypatch.setattr(st, "rehearse", lambda *a, **k: pytest.fail("must refuse before the rehearsal"))
    monkeypatch.setattr(st, "run_all", lambda *a, **k: pytest.fail("must never write the demo without a terminal"))
    with pytest.raises(sp.SeedError, match="interactive terminal"):
        st.cmd_tickets(argparse.Namespace(apply=True))


def test_rehearsal_runs_in_a_scratch_process_and_leaves_the_demo_alone(tmp_path):
    import os
    before = subprocess.run(["git", "-C", str(sp.HARNESS), "status", "--short", "orchestrator"],
                            capture_output=True, text=True).stdout
    root, problems = st.rehearse(st.Refs(_fake_out()), tmp_path / "copy")
    assert (root / "orchestrator" / "config.json").exists() and (root / "scripts" / "seed").is_dir()
    for repo in ("ingest", "dbt", "infra"):
        if (sp.HARNESS / repo).is_dir():
            assert (root / repo).is_dir(), repo
    assert st._copy_ignore(str(sp.HARNESS / "orchestrator" / ".state"), ["locks", "addons", "events.jsonl"]) == \
        ["locks", "addons"]
    assert isinstance(problems, list)
    # the human steps were signed into the scratch ledger of the child, not into this process's user dir
    assert (tmp_path / "orch-user" / "ledger.jsonl").exists()
    assert not (Path(os.environ["ORCH_STATE_DIR"]) / "ledger.jsonl").exists()
    assert subprocess.run(["git", "-C", str(sp.HARNESS), "status", "--short", "orchestrator"],
                          capture_output=True, text=True).stdout == before


def test_human_steps_are_refused_under_an_agent_ancestor(demo_ws, monkeypatch):
    import orch.actor
    from orch.errors import HumanOnlyError
    monkeypatch.setattr(orch.actor, "process_chain", lambda: [(1, "claude --resume")])
    with pytest.raises(HumanOnlyError, match="agent harness"):
        st.migrate_external(demo_ws, st.Ops(demo_ws, st.HUMAN))


def test_refresh_needs_signed_decisions(demo_ws, monkeypatch, capsys):
    import argparse
    monkeypatch.setattr(sp, "HARNESS", demo_ws.root)
    missing = st.unsigned_on(demo_ws)
    assert missing and set(missing) <= set(ss.REFRESH)
    assert st.cmd_refresh(argparse.Namespace(apply=False)) == 0
    assert "SKIP" in capsys.readouterr().out
    assert st.cmd_refresh(argparse.Namespace(apply=True)) == 1
    assert "orch ledger adopt" in capsys.readouterr().err


def test_apply_refuses_unsigned_decisions_before_the_rehearsal(demo_ws, monkeypatch):
    import argparse
    import orch.actor
    monkeypatch.setattr(sp, "HARNESS", demo_ws.root)
    monkeypatch.setattr(orch.actor, "require_human_terminal", lambda *a, **k: None)
    monkeypatch.setattr(st, "rehearse", lambda *a, **k: pytest.fail("must refuse before the rehearsal"))
    with pytest.raises(sp.SeedError, match="orch ledger adopt"):
        st.cmd_tickets(argparse.Namespace(apply=True))


def test_every_human_decision_passes_the_hash_of_what_was_shown(demo_ws, monkeypatch):
    """orch refuses a human decision without the hash of what the human read: the seed computes it with orch's own
    functions and passes it on every approve, answer, verdict and request-changes."""
    from orch.core.ops import Ops
    seen = []
    for name in ("approve", "answer", "verdict", "request_changes"):
        real = getattr(Ops, name)

        def spy(self, *a, _real=real, _name=name, **kw):
            seen.append((_name, kw.get("expected_hash")))
            return _real(self, *a, **kw)
        monkeypatch.setattr(Ops, name, spy)
    _build(demo_ws)
    assert {n for n, _ in seen} == {"approve", "answer", "verdict", "request_changes"}
    assert all(h and h.startswith("sha256:") for _, h in seen)


def test_artifacts_are_linked_and_the_inline_image_is_pinned(demo_ws):
    from orch.core import store
    from orch.core.artifacts import doc_items
    from orch.core.gates import gate_hash, gate_meta, gate_state
    _build(demo_ws)
    t = store.load(demo_ws, "DEMO-0023")[1]
    entry = next(e for e in t.meta["artifacts"] if e["name"] == "daily-report-mockup.png")
    assert (entry["kind"], entry["ac"]) == ("screenshot", 1) and entry["sha256"]
    assert "(artifact:daily-report-mockup.png)" in t.section("Requirements")
    assert ("artifact daily-report-mockup.png", f"sha256:{entry['sha256']}") in gate_meta(t, "requirements")
    assert gate_state(t, "requirements") == "approved" and t.meta["gates"]["requirements"]["hash"] == gate_hash(t, "requirements")
    linked = {k: [i.get("name") or i.get("url") for i in doc_items(store.load(demo_ws, k)[1])]
              for k in ("DEMO-0020", "DEMO-0027", "DEMO-0028", "DEMO-0029")}
    assert all(linked.values())
    assert any(i.get("task") == "T2" for i in doc_items(store.load(demo_ws, "DEMO-0028")[1]))


def test_run_works_right_after_ledger_adopt(demo_ws):
    """The documented flow: `orch ledger adopt --workspace`, then run again. The adopt events are stamped now, so a
    window that started at the last event would be negative; the seed starts it at the last non-adopt event."""
    import seed_checklist as cl
    import seed_scratch
    from orch.core import store
    from orch.core.events import scan_events
    from orch.core.ops import claim_expired
    adopted, refused = seed_scratch.sign_unsigned(demo_ws, st.HUMAN)
    assert adopted and not refused
    assert any(e.kind == "ledger.adopted" for e in scan_events(demo_ws).events)
    ids = _build(demo_ws)
    assert len(ids) == 21 and cl.ticket_problems(demo_ws) == []
    scan = scan_events(demo_ws)
    assert not scan.tampered and not scan.gaps  # orch accepts the log: seq is contiguous
    for key in ss.STALE:
        assert claim_expired(store.load(demo_ws, key)[1].meta["claim"], 4), key
