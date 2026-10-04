import json

import seed_checklist as cl


def _ws(tmp_path):
    from orch.testing.workspace import fake_workspace
    return fake_workspace(tmp_path / "ws", tickets=[{"title": "Only one", "status": "backlog"}]).ws


def test_a_bare_workspace_misses_almost_everything(tmp_path):
    problems = "\n".join(cl.ticket_problems(_ws(tmp_path)))
    for word in ("type: missing", "status: missing", "plan: missing", "claim: missing fresh, stale",
                 "tasks: missing", "blocked_by: longest chain is 0"):
        assert word in problems


def test_chain_depth_counts_tickets_in_the_longest_chain():
    meta = {"A": {"blocked_by": []}, "B": {"blocked_by": ["A"]}, "C": {"blocked_by": ["B"]}, "D": {"blocked_by": ["X"]}}
    assert cl.chain_depth(meta) == 3


def test_chain_depth_survives_a_cycle():
    assert cl.chain_depth({"A": {"blocked_by": ["B"]}, "B": {"blocked_by": ["A"]}}) == 2


def test_expected_findings_file_is_valid():
    data = json.loads((cl.sp.HERE / "expected_findings.json").read_text())
    assert set(data) == {"claim-expired", "gate-invalidated", "task-doing-stale", "delegated-approval"}
    assert all(v["why"] for v in data.values())


def test_allowed_findings_do_not_fail_the_checklist(monkeypatch, capsys):
    import orch.core.workspace as owk
    monkeypatch.setattr(owk.Workspace, "open", staticmethod(lambda path: None))
    monkeypatch.setattr(cl, "CHECKS", [lambda ws: [cl.Allowed("approved: not seeded")]])
    assert cl.cmd_checklist(None) == 0
    assert "ALLOWED" in capsys.readouterr().out
    monkeypatch.setattr(cl, "CHECKS", [lambda ws: [cl.Allowed("x"), "real problem"]])
    assert cl.cmd_checklist(None) == 1
